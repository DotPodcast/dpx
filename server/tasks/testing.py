from . import RunnerBase
from uuid import uuid4
from importlib import import_module


class TestRunner(RunnerBase):
    RESULT = True

    def run(self, func, *args, **kwargs):
        module, func = func.rsplit('.', 1)
        module = import_module(module)
        f = getattr(module, func)
        f(*args, **kwargs)
        return str(uuid4())

    def get(self, id):
        return self.RESULT
