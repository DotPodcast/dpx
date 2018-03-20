from api import task
import requests_mock


class MockJob(object):
    id = 'foo'


def test_successful_task():
    def f(task):
        return 'All is well.'

    t = task(f)
    t.job = MockJob()

    response = {
        'id': 'foo',
        'status': 'finished'
    }

    with requests_mock.mock() as m:
        m.post(
            'http://server/api/v1/tasks/foo/',
            json=response
        )

        assert t(api_access_key='bar') == response


def test_failed_task():
    def f(task):
        raise Exception('All is lost.')

    t = task(f)
    t.job = MockJob()
    t.__api_key = 'bar'

    response = {
        'id': 'foo',
        'status': 'failed'
    }

    with requests_mock.mock() as m:
        m.post(
            'http://server/api/v1/tasks/foo/',
            json=response
        )

        assert t(api_access_key='bar') == response


def test_progress():
    def f(task):
        for i in range(0, 100):
            task.progress(i, i)

    t = task(f)
    t.job = MockJob()
    t.__api_key = 'bar'

    response = {
        'id': 'foo',
        'status': 'failed'
    }

    with requests_mock.mock() as m:
        m.post(
            'http://server/api/v1/tasks/foo/',
            json=response
        )

        assert t(api_access_key='bar') == response
