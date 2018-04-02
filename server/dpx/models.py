from bs4 import BeautifulSoup
from django.conf import settings as site_settings
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.http import urlencode
from mimetypes import guess_extension
from tasks.signals import *
from . import helpers, query, settings, IMPORT_TASK_NAME
import json


class Account(models.Model):
    owner = models.ForeignKey('auth.User', related_name='accounts')


class Person(models.Model):
    account = models.ForeignKey(Account, related_name='people')
    slug = models.CharField(max_length=36)
    name = models.CharField(max_length=100)
    url = models.URLField('URL', max_length=512, null=True, blank=True)

    public_key = models.CharField(
        max_length=500, db_index=True, null=True, blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                self.account.people.all(),
                self.pk is None,
                self.name
            )

        super().save(*args, **kwargs)

    def as_dict(self, request):
        def get_url():
            site = Site.objects.get_current()
            return request.build_absolute_uri(
                reverse('author', args=[self.slug])
            )

        return {
            'name': self.name,
            'url': self.url or get_url(),
            'avatar': (
                'https://gravatar.com/avatar?s=300&d=mm'
            )
        }

    class Meta:
        ordering = ('name',)
        unique_together = ('slug', 'account')


class Publisher(models.Model):
    account = models.ForeignKey(Account, related_name='publishers')
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=512, null=True, blank=True)
    logo = models.URLField(max_length=512, null=True, blank=True)
    admins = models.ManyToManyField(site_settings.AUTH_USER_MODEL, related_name='publishers')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Author(Person):
    user = models.OneToOneField(site_settings.AUTH_USER_MODEL, related_name='author')

    def as_dict(self, request):
        data = super().as_dict(request)
        data['email'] = self.user.email

        return data


class Taxonomy(models.Model):
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Term(models.Model):
    taxonomy = models.ForeignKey(Taxonomy, related_name='terms')
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=512, unique=True)
    description = models.TextField(null=True, blank=True)

    objects = query.TermQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Host(Person):
    user = models.OneToOneField(
        site_settings.AUTH_USER_MODEL, related_name='host', null=True, blank=True
    )


class Podcast(models.Model):
    account = models.ForeignKey(Account, related_name='podcasts')
    name = models.CharField(max_length=300)
    slug = models.CharField(max_length=100, unique=True, editable=False)
    remote_feed = models.URLField(
        max_length=512, null=True, blank=True, db_index=True
    )

    subtitle = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        Author, related_name='podcasts', null=True, blank=True
    )

    remote_artwork = models.URLField(
        max_length=512,
        null=True,
        blank=True
    )

    banner_image = models.URLField(max_length=512, null=True, blank=True)
    publisher = models.ForeignKey(Publisher, related_name='podcasts')
    hosts = models.ManyToManyField(Host, through='PodcastHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='podcasts')

    objects = query.PodcastQuerySet.as_manager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                self.account.podcasts.all(),
                self.pk is None,
                self.name
            )

        super().save(*args, **kwargs)

    def get_description_plain(self):
        return ' '.join(
            BeautifulSoup(
                self.description,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_previous_url(self, page, request):
        if page.has_previous():
            return '%s?%s' % (
                self.get_feed_body_url(request),
                urlencode(
                    {
                        'page': page.previous_page_number()
                    }
                )
            )

    def get_next_url(self, page, request):
        if page.has_next():
            return '%s?%s' % (
                self.get_feed_body_url(request),
                urlencode(
                    {
                        'page': page.next_page_number()
                    }
                )
            )

    def get_home_page_url(self, request):
        return request.build_absolute_uri(
            '/%s/' % self.slug
        )

    def get_feed_head_url(self, request):
        return request.build_absolute_uri(
            reverse('podcast_feed_head', args=[self.slug])
        )

    def get_feed_body_url(self, request):
        return request.build_absolute_uri(
            reverse('podcast_feed_body', args=[self.slug])
        )

    def get_subscription_url(self, request):
        return request.build_absolute_uri(
            reverse('podcast_subscribe', args=[self.slug])
        )

    def head_dict(self, request):
        return {
            'version': settings.DOTPODCAST_VERSION,
            'title': self.name,
            'home_page_url': self.get_home_page_url(request),
            'meta_url': self.get_feed_head_url(request),
            'items_url': self.get_feed_body_url(request),
            'subscription_url': self.get_subscription_url(request),
            'description': self.subtitle,
            'user_comment': settings.USER_COMMENT,
            'author': self.author and self.author.as_dict(request) or None,
            'expired': False,
            'subtitle': self.subtitle,
            'taxonomy_terms': list(
                self.taxonomy_terms.values_list(
                    'url', flat=True
                )
            ),
            'artwork': {
                '@1x': self.remote_artwork,
                '@2x': self.remote_artwork
            },
            'description_text': self.get_description_plain(),
            'description_html': self.description,
            'payment_addresses': dict(
                self.wallets.values_list(
                    'symbol',
                    'address'
                )
            )
        }

    def body_dict(self, request, page=1):
        episodes = self.episodes.select_related().prefetch_related().published()
        paginator = Paginator(
            episodes,
            settings.EPISODES_PER_PAGE
        )

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        meta = {
            'version': settings.DOTPODCAST_VERSION,
            'total_count': episodes.count(),
            'per_page': settings.EPISODES_PER_PAGE
        }

        next_url = self.get_next_url(page_obj, request)
        if next_url:
            meta['next_url'] = next_url

        previous_url = self.get_previous_url(page_obj, request)
        if previous_url:
            meta['previous_url'] = previous_url

        return {
            'meta': meta,
            'items': [
                episode.as_dict(request)
                for episode in page_obj.object_list
            ]
        }

    def dump_head_json(self, request, stream):
        json.dump(
            self.head_dict(request),
            stream,
            ensure_ascii=False,
            indent=4
        )

    def dump_body_json(self, request, stream, page=1):
        json.dump(
            self.body_dict(request, page=page),
            stream,
            ensure_ascii=False,
            indent=4
        )

    def subscribe(
        self, kind, token,
        app_name='', app_url='', app_logo='',
        activity='listen'
    ):
        if kind == 'preview':
            for player in self.players.filter(app_url=app_url):
                return player

            player = self.players.create(
                app_name=app_name,
                app_url=app_url,
                app_logo=app_logo
            )

            player.full_clean()
            return player

        if kind == 'download':
            try:
                activity_kind = {
                    'listen': 'c',
                    'subscribe': 's',
                    '': None
                }[activity]
            except KeyError:
                raise ValidationError('Invalid activity.')

            for subscription in self.subscribers.filter(source_token=token):
                if activity_kind:
                    subscription.kind = activity_kind
                    subscription.full_clean()
                    subscription.save()

                return subscription

            subscriber = self.subscribers.create(
                app_name=app_name,
                app_url=app_url,
                app_logo=app_logo,
                source_token=token,
                kind=activity_kind or 'listen'
            )

            subscriber.full_clean()
            return subscriber

        if kind == 'transit':
            raise NotImplementedError('Transit tokens not yet implemented.')

    class Meta:
        ordering = ('name',)


class Wallet(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='wallets')
    symbol = models.CharField(
        max_length=30,
        choices=(
            ('bch', 'Bitcoin Cash'),
            ('btc', 'Bitcoin'),
            ('eth', 'Ethereum'),
            ('ltc', 'Litecoin'),
            ('xrp', 'Ripple'),
            ('zec', 'Zcash')
        )
    )

    address = models.CharField(max_length=128)

    def __unicode__(self):
        return self.get_symbol_display()

    class Meta:
        unique_together = ('symbol', 'podcast')


class PodcastHost(models.Model):
    podcast = models.ForeignKey(Podcast)
    host = models.ForeignKey(Host, related_name='podcasts')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'podcast')


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Season(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='seasons')
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('number',)


class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='episodes')
    remote_id = models.CharField(
        'remote ID', max_length=512, null=True, blank=True, db_index=True
    )

    slug = models.CharField(max_length=100, editable=False)
    title = models.CharField(max_length=500)
    subtitle = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)

    remote_artwork = models.URLField(
        max_length=512,
        null=True,
        blank=True
    )

    banner_image = models.URLField(max_length=512, null=True, blank=True)
    date_published = models.DateTimeField()
    date_modified = models.DateTimeField(
        auto_now=True, null=True, blank=True
    )

    audio_mimetype = models.CharField(max_length=50, null=True, blank=True)
    audio_duration = models.PositiveIntegerField(null=True, blank=True)
    audio_filesize = models.PositiveIntegerField(null=True, blank=True)

    video_mimetype = models.CharField(max_length=50, null=True, blank=True)
    video_duration = models.PositiveIntegerField(null=True, blank=True)
    video_filesize = models.PositiveIntegerField(null=True, blank=True)

    remote_audio_enclosure = models.URLField(
        max_length=512, null=True, blank=True
    )

    remote_video_enclosure = models.URLField(
        max_length=512, null=True, blank=True
    )

    season = models.ForeignKey(
        Season, related_name='episodes', null=True, blank=True
    )

    number = models.PositiveIntegerField(default=0)
    hosts = models.ManyToManyField(Host, through='EpisodeHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='episodes')

    objects = query.EpisodeQuerySet.as_manager()

    def __str__(self):
        return self.title

    def download(self, kind):
        if kind == 'audio':
            url = self.remote_audio_enclosure
            mime_type = self.audio_mimetype
            file_size = self.audio_filesize
        elif kind == 'video':
            url = self.remote_video_enclosure
            mime_type = self.video_mimetype
            file_size = self.video_filesize
        else:
            raise Exception('Unknown media kind')

        return {
            'url': url,
            'mime_type': mime_type,
            'file_size': file_size
        }

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                self.podcast.episodes,
                self.pk is None,
                self.title
            )

        super().save(*args, **kwargs)

    def get_page_url(self, request):
        return request.build_absolute_uri(
            '/%s/%s/' % (self.podcast.slug, self.slug)
        )

    def get_body_plain(self):
        return ' '.join(
            BeautifulSoup(
                self.body,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_download_url(self, kind, request):
        mime_type = getattr(self, '%s_mimetype' % kind)
        extension = guess_extension(mime_type)[1:]

        return request.build_absolute_uri(
            reverse(
                'episode_quickplay',
                args=[self.podcast.slug, self.pk, kind, extension]
            )
        )

    def as_dict(self, request):
        data = {
            'id': self.get_page_url(request),
            'url': self.get_page_url(request),
            'title': self.title,
            'content_text': self.get_body_plain(),
            'content_html': self.body,
            'summary': self.summary,
            'image': self.remote_artwork,
            'date_published': self.date_published.replace(
                microsecond=0
            ).isoformat(),
            'author': self.podcast.author.as_dict(request)
        }

        if self.subtitle:
            data['subtitle'] = self.subtitle

        if self.season:
            data['season_number'] = self.season.number

        if self.number:
            data['episode_number'] = self.number

        if self.remote_audio_enclosure:
            data['content_audio'] = {
                'mime_type': self.audio_mimetype,
                'duration': self.audio_duration,
                'url': self.get_download_url('audio', request),
                'file_size': self.audio_filesize
            }

        if self.remote_video_enclosure:
            data['content_video'] = {
                'mime_type': self.video_mimetype,
                'duration': self.video_duration,
                'url': self.get_download_url('video', request),
                'file_size': self.video_filesize
            }

        if self.date_modified:
            data['date_modified'] = self.date_modified.replace(
                microsecond=0
            ).isoformat()

        return data

    class Meta:
        unique_together = ('slug', 'podcast')
        ordering = ('-date_published',)
        get_latest_by = 'date_published'


class EpisodeHost(models.Model):
    episode = models.ForeignKey(Episode)
    host = models.ForeignKey(Host, related_name='hosted_episodes')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'episode')


class EpisodeGuest(models.Model):
    episode = models.ForeignKey(Episode)
    person = models.ForeignKey(Person, related_name='guesting_episodes')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('person', 'episode')


class TokenPair(models.Model):
    public_token = models.CharField(max_length=64, unique=True)
    secret_token = models.CharField(max_length=256, unique=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = helpers.create_token(32)

        if not self.secret_token:
            self.secret_token = helpers.create_token(128, True)

        super().save(*args, **kwargs)


class Subscriber(TokenPair):
    podcast = models.ForeignKey(Podcast, related_name='subscribers')
    app_name = models.CharField(max_length=100, null=True, blank=True)
    app_url = models.URLField(u'app URL', max_length=512, null=True, blank=True)
    app_logo = models.URLField(max_length=512, null=True, blank=True)
    kind = models.CharField(max_length=1,
        choices=(
            ('c', 'casual listener'),
            ('s', 'subscriber')
        )
    )

    source_token = models.CharField(max_length=255)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or self.public_token

    def as_dict(self):
        return {
            'subscriber_token': self.public_token,
            'subscriber_secret': self.secret_token
        }

    class Meta:
        ordering = ('-last_fetched', '-date_subscribed')
        unique_together = ('source_token', 'podcast')


class Player(TokenPair):
    podcast = models.ForeignKey(Podcast, related_name='players')
    app_name = models.CharField(max_length=100, null=True, blank=True)
    app_url = models.URLField(u'app URL', max_length=512)
    app_logo = models.URLField(max_length=512, null=True, blank=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or self.app_url

    def as_dict(self):
        return {
            'preview_token': self.public_token,
            'preview_secret': self.secret_token
        }

    class Meta:
        ordering = ('-last_fetched',)
        unique_together = ('app_url', 'podcast')


@receiver(job_finished)
def import_job_finished(sender, func, **kwargs):
    if func == IMPORT_TASK_NAME:
        pass
    pass


@receiver(job_progress)
def import_job_progress(sender, func, **kwargs):
    if func == IMPORT_TASK_NAME:
        passpass


@receiver(job_failed)
def import_job_failed(sender, func, **kwargs):
    if func == IMPORT_TASK_NAME:
        passpass
