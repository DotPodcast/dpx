from importers.rss import RssImporter
from importing import get_feed_stream, get_feed_data
from os import path
import exceptions
import pytest
import requests_mock


IMPORTER = RssImporter
RSS_URL = 'https://post.futurimedia.com/ksteam/playlist/rss/12.xml?show_deleted=true'
RSS_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'armstrongandgetty',
    'feed.xml'
)

DESCRIPTION_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'armstrongandgetty',
    'description.txt'
)

ITUNES_SUMMARY_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'armstrongandgetty',
    'itunes_summary.txt'
)


def test_valid_feed():
    stream = open(RSS_FILENAME, 'r')

    (
        importer,
        feed,
        terms,
        metadata,
        items
    ) = get_feed_data(stream)

    assert sorted(list(terms)) == [
        'https://dotpodcast.co/taxonomies/language/#en_us',
        'https://dotpodcast.co/taxonomies/profanity/#none',
        'https://dotpodcast.co/taxonomies/subject/#comedy',
        'https://dotpodcast.co/taxonomies/subject/#news'
    ]

    assert metadata == {
        'title': 'Armstrong and Getty',
        'author': '',
        'explicit': 'no',
        'copyright': '',
        'description': 'Armstrong and Getty 6am-10am weekday mornings',
        'image': 'https://post.futurimedia.com/ksteam/playlist/streamon-perm/ksteam-1400x1400.jpg',
        'language': 'en-us',
        'link': '',
        'owner_email': '',
        'owner_name': '',
        'subtitle': '',
        'summary': ''
    }

    for item in items:
        with requests_mock.mock() as m:
            m.head(
                'https://post.futurimedia.com/ksteam/playlist/12/954.m4a',
                headers={
                    'Content-Length': '13743537'
                }
            )

            assert importer.get_item_data(feed, item) == {
                'id': 'https://post.futurimedia.com/ksteam/playlist/12/954.m4a',
                'url': 'https://post.futurimedia.com/ksteam/playlist/12/954.m4a',
                'title': '3/16/18 AG Hr. 4 This Will Not Stand',
                'subtitle': '',
                'season_number': '',
                'episode_number': '',
                'date': 'Fri, 16 Mar 2018 10:21:17 -0700',
                'description': open(DESCRIPTION_FILENAME, 'r').read().strip(),
                'summary': open(ITUNES_SUMMARY_FILENAME, 'r').read().strip(),
                'keywords': '',
                'enclosure_url': 'https://post.futurimedia.com/ksteam/playlist/12/954.m4a',
                'enclosure_type': 'audio/mp4',
                'enclosure_size': 13743537,
                'enclosure_duration': '00:37:37',
                'image': ''
            }

        break

    assert type(importer) == IMPORTER
