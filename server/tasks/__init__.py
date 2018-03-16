from django.conf import settings
from rq import Queue
from redis import Redis


def run(func, *args, **kwargs):
    q = Queue(connection=Redis.from_url(settings.REDIS_URL))
    return q.enqueue(func, args=args, kwargs=kwargs)
