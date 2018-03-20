from django.conf import settings
from importlib import import_module


TASK_RUNNER, TASK_OPTIONS = getattr(
    settings,
    'TASK_RUNNER',
    (
        'tasks.redis.RedisRunner',
        {
            'REDIS_URL': getattr(settings, 'REDIS_URL', None)
        }
    )
)


class RunnerBase(object):
    def __init__(self, **options):
        for key, value in options.items():
            setattr(self, key.upper(), value)


def get_runner():
    module, klass = TASK_RUNNER.rsplit('.', 1)
    module = import_module(module)
    klass = getattr(module, klass)

    return klass(**TASK_OPTIONS)


def run(func, *args, **kwargs):
    runner = get_runner()
    return runner.run(func, *args, **kwargs)


def get(id):
    runner = get_runner()
    return runner.get(id)
