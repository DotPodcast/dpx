from bs4 import BeautifulSoup
from bs4.element import NavigableString


class XmlMixin(object):
    def apply(self, data):
        return BeautifulSoup(data, 'xml')

    def get_first_tag(self, dom, tag, default=None, recursive=True):
        item = dom.find(tag)
        if item is not None:
            if recursive or item.parent == dom:
                return item

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_text(self, dom, tag, default=None, recursive=True):
        item = dom.find(tag)

        if item is not None:
            if recursive or item.parent == dom:
                return item.text

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_html(self, dom, tag, default=None, recursive=True):
        item = dom.find(tag)

        if item is not None:
            if recursive or item.parent == dom:
                return '\n\n'.join(
                    [
                        isinstance(s, NavigableString) and s.string or s.get_text() or ''
                        for s in item.contents
                    ]
                )

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_attr(self, dom, tag, attribute, default='', recursive=True):
        item = dom.find(tag)
        value = None

        if item is not None:
            if not recursive and item.parent != dom:
                item = None

        if item is not None:
            try:
                value = item[attribute]
            except KeyError:
                pass
        else:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        if value is not None:
            return value

        if default is not None:
            return default

        raise Exception(
            'Node <%s> does not have expected attribute %s' % (
                item.name, attribute
            )
        )
