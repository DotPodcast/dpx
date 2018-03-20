from importing import get_feed_stream, get_feed_data
from io import StringIO
import exceptions
import pytest
import requests_mock


RSS_URL_NOTFOUND = 'https://feeds.podiant.co/leopard/feed.xml'


def test_get_invalid_stream():
    with pytest.raises(exceptions.ImportingHTTPError) as ex:
        stream = get_feed_stream('invalid://url')

    assert (
        'No connection adapters were found for \'invalid://url\''
    ) in str(ex.value)


def test_get_notfound_stream():
    with requests_mock.mock() as m:
        m.get(RSS_URL_NOTFOUND, status_code=404)
        with pytest.raises(exceptions.ImportingHTTPError) as ex:
            stream = get_feed_stream(RSS_URL_NOTFOUND)

        assert (
            '404 Client Error: None for url: %s' % RSS_URL_NOTFOUND
        ) in str(ex.value)


def test_invalid_feed():
    with pytest.raises(exceptions.ImportingError) as ex:
        get_feed_data(
            StringIO('invalid data')
        )

    assert 'No importer could process the source feed.' in str(ex.value)
