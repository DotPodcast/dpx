from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from .settings import DOTPODCAST_DOMAIN
import re


TAXONOMY_PATTERNS = {
    'Subject': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/subject/)#([\w-]+)$'),
    'Language': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/language/)#([\w-]+)$'),
    'Profanity': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/profanity/)#([\w-]+)$')
}


class PodcastQuerySet(QuerySet):
    pass


class TermQuerySet(QuerySet):
    pass
    # @transaction.atomic()
    # def infer(self, url):
    #     from .models import Taxonomy
    #
    #     for obj in self.filter(url__iexact=url):
    #         return obj
    #
    #     for taxonomy, pattern in TAXONOMY_PATTERNS.items():
    #         match = pattern.match(url)
    #         if match is not None:
    #             tax_url, term_slug = match.groups()
    #             term_name = term_slug.replace('-', ' ').capitalize()
    #
    #             try:
    #                 tax = Taxonomy.objects.get(url__iexact=tax_url)
    #             except Taxonomy.DoesNotExist:
    #                 tax = Taxonomy.objects.create(
    #                     name=taxonomy,
    #                     url=tax_url
    #                 )
    #
    #             return self.create(
    #                 name=term_name,
    #                 url=url,
    #                 taxonomy=tax
    #             )
    #
    #     raise ValidationError(
    #         'Third-party taxonomies are currently not supported.'
    #     )


class EpisodeQuerySet(QuerySet):
    def published(self):
        return self.filter(
            date_published__lte=timezone.now()
        )
