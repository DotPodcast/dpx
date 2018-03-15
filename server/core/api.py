from django.conf.urls import url
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.core.validators import validate_email
from django.db import transaction
from tastypie.http import (
    HttpUnauthorized, HttpForbidden, HttpUnprocessableEntity
)

from tastypie.resources import Resource
from tastypie.utils import trailing_slash
from api.v1 import v1_api


class UserResource(Resource):
    def prepend_urls(self):
        return [
            url(
                r'^(?P<resource_name>%s)%s$' % (
                    self._meta.resource_name,
                    trailing_slash()
                ),
                self.wrap_view('post_list'),
                name='api_user'
            ),
            url(
                r'^(?P<resource_name>%s)/login%s$' % (
                    self._meta.resource_name,
                    trailing_slash()
                ),
                self.wrap_view('login'),
                name='api_login'
            )
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(
            request,
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json')
        )

        user = authenticate(
            email=data.get('email', ''),
            password=data.get('password', '')
        )

        if user and user.is_active:
            login(request, user)

            return self.create_response(
                request,
                {
                    'id': 'me',
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )

        return self.create_response(
            request,
            {
                'reason': 'Invalid email address or password.'
            },
            HttpUnauthorized
        )

    def get_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        if request.user.is_anonymous:
            return self.create_response(
                request,
                {
                    'reason': 'Session cookie invalid.'
                },
                HttpUnauthorized
            )

        return self.create_response(
            request,
            {
                'id': 'me',
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name
            }
        )

    @transaction.atomic()
    def post_list(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(
            request,
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json')
        )

        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not email:
            return self.create_response(
                request,
                {
                    'reason': 'Email is invalid.',
                    'errors': {
                        'email': ['This field is required.']
                    }
                },
                HttpUnprocessableEntity
            )

        if not password:
            return self.create_response(
                request,
                {
                    'reason': 'Password is invalid.',
                    'errors': {
                        'password': ['This field is required.']
                    }
                },
                HttpUnprocessableEntity
            )

        if User.objects.filter(email__iexact=email):
            return self.create_response(
                request,
                {
                    'reason': 'Email is invalid.',
                    'errors': {
                        'email': [
                            'A user already exists with this email address.'
                        ]
                    }
                },
                HttpUnprocessableEntity
            )

        try:
            validate_email(email)
        except ValidationError as ex:
            return self.create_response(
                request,
                {
                    'reason': 'Email is invalid.',
                    'errors': {
                        'email': ex.messages
                    }
                },
                HttpUnprocessableEntity
            )

        try:
            validate_password(password)
        except ValidationError as ex:
            return self.create_response(
                request,
                {
                    'reason': 'Password is invalid.',
                    'errors': {
                        'password': ex.messages
                    }
                },
                HttpUnprocessableEntity
            )

        user = User.objects.create_user(
            email,
            email,
            password
        )

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        user.full_clean()
        user.save()

        response = self.create_response(
            request,
            {
                'id': 'me',
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )

        response['Location'] = reverse('api_user', args=['v1', 'user'])
        response.status_code = 201
        return response

    class Meta:
        queryset = User.objects.all()
        fields = ('first_name', 'last_name', 'emakl')


v1_api.register(UserResource())
