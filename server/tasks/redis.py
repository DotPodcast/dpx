from django.conf import settings
from redis import Redis
from rq import Queue
from . import RunnerBase


class RedisRunner(RunnerBase):
    def run(self, func, *args, **kwargs):
        q = Queue(connection=Redis.from_url(settings.REDIS_URL))
        return q.enqueue(func, args=args, kwargs=kwargs)

    def get(id):
        q = Queue(connection=Redis.from_url(settings.REDIS_URL))
        return q.get_job(id).meta
