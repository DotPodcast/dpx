from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from logging import getLogger
from rq import Queue
from rq.job import JobStatus
from redis import Redis
from .signals import job_finished, job_failed, job_progress
import realtime


class TaskView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_job(self, guid):
        q = Queue(connection=Redis.from_url(settings.REDIS_URL))
        job = q.fetch_job(guid)

        if job is None:
            raise NotFound('Job not found.')

        return job

    def dispatch(self, request, guid=None, **kwargs):
        self.job = self.get_job(guid)
        return super().dispatch(request, guid, **kwargs)

    def get(self, request, guid=None, **kwargs):
        kw = dict(**self.job.kwargs)
        if 'api_access_key' in kw:
            del kw['api_access_key']

        return Response(
            {
                'id': self.job.id,
                'status': self.job.status,
                'args': self.job.args,
                'kwargs': kw,
                'info': self.job.meta
            }
        )

    def update_meta(self, source, dest):
        for key, value in dest.items():
            if key.startswith('+'):
                if key[1:] in source:
                    if not isinstance(source[key[1:]], list):
                        raise ValidationError(
                            'Cannot append to %s, as it is not a list' % (
                                key[1:]
                            )
                        )

                    source[key[1:]].append(value)
                else:
                    source[key[1:]] = [value]
            elif isinstance(value, dict):
                if key in source:
                    self.update_meta(
                        source[key],
                        value
                    )
                else:
                    source[key] = value
            else:
                source[key] = value

    def post(self, request, guid=None, **kwargs):
        status = request.data.get('status')
        data = request.data.get('data')

        if status is None:
            raise ValidationError(
                {
                    'status': ['Specify a value.']
                }
            )

        if not hasattr(JobStatus, status.upper()):
            if status != 'running':
                raise ValidationError(
                    {
                        'status': ['Specify a valid value.']
                    }
                )

        if data is None:
            raise ValidationError(
                {
                    'data': ['Specify a value.']
                }
            )

        realtime.push(data, 'tasks:%s' % self.job.id)
        self.update_meta(self.job.meta, data)
        self.job.save()

        if status == JobStatus.FINISHED:
            signal = job_finished
        elif status == JobStatus.FINISHED:
            signal = job_failed
        elif status == 'running':
            signal = job_progress
        else:
            signal = None

        if signal is not None:
            logger = getLogger('tasks')

            try:
                signal.send(
                    sender=type(self),
                    func=self.job._func_name,
                    args=self.job.args,
                    kwargs=self.job.kwargs,
                    data=data
                )
            except Exception as ex:
                logger.error(str(ex), exc_info=True)

        return Response(
            {
                'id': self.job.id,
                'status': self.job.status
            }
        )
