from . import ImporterBase
from .xml import XmlMixin
from bs4 import BeautifulSoup
from mimetypes import guess_type
from urllib.parse import urlparse
import requests


class RssImporter(XmlMixin, ImporterBase):
    verbose_name = 'RSS'

    def apply(self, data):
        root = super().apply(data)

        if root is not None:
            actual_item_count = data.count('</item>')
            found_item_count = len(root.findAll('item'))

            if found_item_count == actual_item_count:
                for child in root.findChildren():
                    channel = self.get_first_tag(child, 'channel', False)
                    if channel is not False:
                        return child

    def get_podcast_data(self, root):
        channel = self.get_first_tag(root, 'channel')
        image = self.get_first_tag(channel, 'itunes:image', False, recursive=False)
        owner = self.get_first_tag(channel, 'itunes:owner', False, recursive=False)
        link = self.get_first_tag(channel, 'atom:link', False, recursive=False)

        return {
            'title': self.first_tag_text(channel, 'title').strip(),
            'subtitle': self.first_tag_text(channel, 'itunes:subtitle', '').strip(),
            'author': self.first_tag_text(
                channel, 'itunes:author', ''
            ).strip(),
            'copyright': self.first_tag_text(channel, 'copyright', '', recursive=False).strip(),
            'owner_name': owner and self.first_tag_text(owner, 'itunes:name', '', recursive=False).strip() or '',
            'owner_email': owner and self.first_tag_text(owner, 'itunes:email', '', recursive=False).strip() or '',
            'summary': self.first_tag_text(channel, 'itunes:summary', '', recursive=False).strip(),
            'description': self.first_tag_text(channel, 'description', '', recursive=False).strip(),
            'language': self.first_tag_text(channel, 'language', '', recursive=False).strip(),
            'explicit': self.first_tag_text(channel, 'itunes:explicit', '', recursive=False).strip(),
            'link': link and link.get('href') or '',
            'image': image and image.get('href') or ''
        }

    def get_categories(self, root):
        channel = self.get_first_tag(root, 'channel')
        categories = []

        for child in channel.findAll('itunes:category'):
            if child.parent.name != 'channel':
                continue

            added = False
            cat_name = child.get('text')

            for grandchild in child.findChildren():
                categories.append(
                    (
                        cat_name,
                        grandchild.get('text')
                    )
                )

                added = True
                break

            if not added:
                categories.append(cat_name)

        return categories

    def get_items(self, root):
        channel = self.get_first_tag(root, 'channel')
        for item in channel.findAll('item'):
            if self.get_first_tag(item, 'enclosure', ''):
                yield item

    def get_item_data(self, root, item):
        enclosure_url = self.first_tag_attr(item, 'enclosure', 'url')
        def get_enclosure_type(url):
            enclosure_type = self.first_tag_attr(
                item,
                'enclosure',
                'type'
            )

            if enclosure_type:
                return enclosure_type

            urlparts = urlparse(url)
            mimetype, encoding = guess_type(urlparts.path)

            if mimetype is None:
                response = requests.get(
                    url,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) '
                            'AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 '
                            'Mobile/14A300 Safari/602.1'
                        ),
                        'Accept-Encoding': None
                    },
                    stream=True
                )

                response.raise_for_status()
                return response.headers['content-type']

            return mimetype

        def get_enclosure_size():
            enclosure_size = self.first_tag_attr(
                item,
                'enclosure',
                'length'
            )

            try:
                enclosure_size = int(enclosure_size)
            except:
                enclosure_size = None

            if enclosure_size and enclosure_size >= 480000:
                return int(enclosure_size)

            try:
                response = requests.head(
                    enclosure_url,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) '
                            'AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 '
                            'Mobile/14A300 Safari/602.1'
                        ),
                        'Accept-Encoding': None
                    },
                    allow_redirects=True
                )

                response.raise_for_status()
                return int(response.headers['content-length'])
            except:
                return 28800000

        def get_enclosure_duration(filesize):
            try:
                enclosure_duration = self.first_tag_text(
                    item,
                    'itunes:duration'
                )
            except:
                enclosure_duration = None

            if enclosure_duration and 'NaN' in enclosure_duration:
                enclosure_duration = None

            if not enclosure_duration:
                enclosure_duration = str(int(float(filesize) / 12800.0))
            else:
                enclosure_duration = str(enclosure_duration)

            if ':' in enclosure_duration:
                while enclosure_duration.endswith(':'):
                    enclosure_duration = enclosure_duration[:-1]

                return enclosure_duration

            try:
                return str(int(enclosure_duration))
            except:
                return str(int(float(filesize) / 12800.0))

        image = self.get_first_tag(item, 'itunes:image', False)
        filesize = get_enclosure_size()

        return {
            'id': self.first_tag_text(item, 'guid', '').strip(),
            'url': self.first_tag_text(item, 'link', '').strip(),
            'title': self.first_tag_text(item, 'title').strip(),
            'subtitle': self.first_tag_text(item, 'itunes:subtitle', '').strip(),
            'season_number': self.first_tag_text(item, 'itunes:season', '').strip(),
            'episode_number': self.first_tag_text(item, 'itunes:episode', '').strip(),
            'date': self.first_tag_text(item, 'pubDate', '').strip(),
            'description': '\n'.join(
                line.strip() for line in (
                    self.first_tag_html(
                        item,
                        'content:encoded',
                        ''
                    ) or self.first_tag_text(
                        item,
                        'description',
                        ''
                    ) or self.first_tag_text(
                        item,
                        'summary',
                        ''
                    ) or ''
                ).strip().splitlines()
            ),
            'summary': self.first_tag_text(item, 'itunes:summary', '').strip(),
            'keywords': ', '.join(
                [
                    line.strip()
                    for line in self.first_tag_text(
                        item, 'itunes:keywords', ''
                    ).strip().splitlines()
                ]
            ),
            'enclosure_url': enclosure_url,
            'enclosure_type': get_enclosure_type(enclosure_url),
            'enclosure_size': filesize,
            'enclosure_duration': get_enclosure_duration(filesize),
            'image': image and image.get('href', '').strip() or ''
        }


class RssAsHtmlImporter(RssImporter):
    verbose_name = 'Malformed RSS'

    def apply(self, data):
        root = BeautifulSoup(
            data.replace('<![CDATA[', '').replace(']]>', ''),
            'html.parser'
        )

        if root is not None:
            channel = self.get_first_tag(root, 'channel', False)
            if channel is not False:
                return root
