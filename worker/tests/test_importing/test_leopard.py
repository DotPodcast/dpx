from importers.rss import RssImporter
from importing import get_feed_stream, get_feed_data
from os import path
import exceptions
import pytest
import requests_mock


IMPORTER = RssImporter
RSS_URL = 'http://feeds.podiant.co/leopard/rss.xml'
RSS_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'leopard',
    'feed.xml'
)

CONTENT_ENCODED_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'leopard',
    'content_encoded.html'
)

ITUNES_SUMMARY_FILENAME = path.join(
    path.dirname(__file__),
    '..',
    'fixtures',
    'leopard',
    'itunes_summary.txt'
)


def test_get_valid_stream():
    rss = open(RSS_FILENAME, 'r').read()
    with requests_mock.mock() as m:
        m.get(RSS_URL, text=rss)

        stream = get_feed_stream(RSS_URL)
        assert stream.read() == rss


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
        'https://dotpodcast.co/taxonomies/language/#en_gb',
        'https://dotpodcast.co/taxonomies/profanity/#none',
        'https://dotpodcast.co/taxonomies/subject/#comedy',
        'https://dotpodcast.co/taxonomies/subject/#literature',
        'https://dotpodcast.co/taxonomies/subject/#science'
    ]

    assert metadata == {
        'title': 'Beware of the Leopard',
        'author': 'Bloomsbury.fm',
        'explicit': 'no',
        'copyright': 'Copyright © Bloomsbury Digital',
        'description': (
            '<p>The complete podcast compendium to the science-fiction comedy '
            'series, covering the radio, TV, book and film incarnations of '
            'Douglas Adams\' "trilogy in five parts", alphabetically, from '
            'Arthur to Zaphod and all points in-between.</p>'
        ),
        'image': 'https://com-podiant.ams3.digitaloceanspaces.com/media/spoke/leopard/artwork/595fee6410ad6.png',
        'language': 'en-GB',
        'link': RSS_URL,
        'owner_email': 'mark@bloomsbury.digital',
        'owner_name': 'Mark Steadman',
        'subtitle': 'The Hitchhiker\'s Guide to the Galaxy podcast',
        'summary': (
            'The complete podcast compendium to the science-fiction comedy '
            'series, covering the radio, TV, book and film incarnations of '
            'Douglas Adams\' "trilogy in five parts", alphabetically, from '
            'Arthur to Zaphod and all points in-between.'
        )
    }

    for item in items:
        assert importer.get_item_data(feed, item) == {
            'id': 'ce19b17e-7c7b-407a-88e7-7fc870b524db',
            'url': 'http://btlpodcast.com/e/360a1660c29cee/',
            'title': 'From the Imperial Galaxy to Islington',
            'subtitle': '',
            'season_number': '2',
            'episode_number': '8',
            'date': 'Thu, 15 Mar 2018 00:00:00 +0000',
            'description': open(CONTENT_ENCODED_FILENAME, 'r').read().strip(),
            'summary': open(ITUNES_SUMMARY_FILENAME, 'r').read().strip(),
            'keywords': 'Douglas Adams, hitchhikers guide, h2g2',
            'enclosure_url': 'https://tracking.podiant.co/d/spoke/leopard/episodes/audio/360a15cfe44510.mp3',
            'enclosure_type': 'audio/mpeg',
            'enclosure_size': 25231537,
            'enclosure_duration': '00:35:02',
            'image': 'http://com-podiant.ams3.digitaloceanspaces.com/media/spoke/leopard/artwork/360a15fa648ca0.jpg'
        }

        break

    assert type(importer) == IMPORTER
