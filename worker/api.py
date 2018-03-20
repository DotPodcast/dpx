from rq import get_current_job
import json
import logging
import os
import requests


class task(object):
    def __init__(self, f):
        self.f = f
        self.logger = logging.getLogger('dpx.api')
        self.logger.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
        self.job = get_current_job()
        self.__api_key = os.getenv('API_KEY')

    def __call__(self, *args, **kwargs):
        if 'api_access_key' in kwargs:
            self.__api_key = kwargs.pop('api_access_key')

        try:
            response = self.f(self, *args, **kwargs)
        except Exception as ex:
            self.logger.error(str(ex), exc_info=True)
            return self.error(ex)

        return self.success(response)

    def get_api_host(self):
        return os.getenv('API_ENDPOINT', 'http://server/')

    def get_api_key(self):
        return self.__api_key

    def success(self, data):
        return self.post('success', data)

    def error(self, err):
        return self.post(
            'error',
            {
                'message': str(err)
            }
        )

    def progress(self, value, data={}):
        return self.post(
            'progress',
            dict(
                progress=value,
                **data
            )
        )

    def post(self, kind, data):
        response = requests.post(
            '%sapi/v1/tasks/%s/' % (
                self.get_api_host(),
                self.job.id
            ),
            json={
                'status': {
                    'success': 'finished',
                    'error': 'failed',
                    'progress': 'running'
                }[kind],
                'data': {
                    kind: data
                }
            },
            headers={
                'Authorization': 'Bearer %s' % self.get_api_key()
            }
        )

        response.raise_for_status()
        return response.json()
