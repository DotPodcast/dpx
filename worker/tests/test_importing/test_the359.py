from importers.rss import RssImporter
from importing import get_feed_stream, get_feed_data
from os import path
import exceptions
import pytest


IMPORTER = RssImporter
RSS_URL = 'http://feed.cnet.com/feed/podcast/359-podcast-audio.xml'
RSS_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'the359',
    'feed.xml'
)

DESCRIPTION_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'the359',
    'description.txt'
)

ITUNES_SUBTITLE_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'the359',
    'itunes_summary.txt'
)

ITUNES_SUMMARY_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'the359',
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
        'https://dotpodcast.co/taxonomies/subject/#technology'
    ]

    assert metadata == {
        'title': 'The 3:59',
        'author': 'CNET.com',
        'explicit': 'no',
        'copyright': '2018 CNET.com',
        'description': (
            'CNET reporters Roger Cheng and Ben Fox Rubin tackle the top tech '
            'stories of the day. Don\'t mind their awkwardness.'
        ),
        'image': 'https://cnet3.cbsistatic.com/img/q573HluckZoFLAGo-vRT0pEJxoQ=/1400x1400/2016/02/29/7373afce-e585-468e-98c9-b1fcbab62541/3-591400.jpg',
        'language': 'en-us',
        'link': RSS_URL,
        'owner_email': 'newcnettvfeedback@cnet.com (CNETTV)',
        'owner_name': 'CNET.com',
        'subtitle': 'Tech news, fast. Really',
        'summary': (
            'CNET reporters Roger Cheng and Ben Fox Rubin tackle the top tech '
            'stories of the day. Don\'t mind their awkwardness.'
        )
    }

    for item in items:
        assert importer.get_item_data(feed, item) == {
            'id': 'cd9ae217-c6cf-4b87-8669-ebadd99742aa',
            'url': 'https://podcast-files.cnet.com/podcast/AreAndroidsmartphonesassafeasiPhones_(The3_59,Ep.370).mp3',
            'title': 'Are Android smartphones as safe as iPhones? (The 3:59, Ep. 370)',
            'subtitle': '',
            'season_number': '',
            'episode_number': '',
            'date': 'Thu, 15 Mar 2018 10:21:44 PDT',
            'description': open(DESCRIPTION_FILENAME, 'r').read().strip(),
            'subtitle': open(ITUNES_SUBTITLE_FILENAME, 'r').read().strip(),
            'summary': open(ITUNES_SUMMARY_FILENAME, 'r').read().strip(),
            'keywords': 'CNET, CNETTV',
            'enclosure_url': 'https://podcast-files.cnet.com/podcast/AreAndroidsmartphonesassafeasiPhones_(The3_59,Ep.370).mp3',
            'enclosure_type': 'audio/mpeg',
            'enclosure_size': 6121899,
            'enclosure_duration': '478',
            'image': ''
        }

        break

    assert type(importer) == IMPORTER
