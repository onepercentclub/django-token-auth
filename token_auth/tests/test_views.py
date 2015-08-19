import json
from datetime import datetime, timedelta

from django.test import TestCase, RequestFactory
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model

import mock

import bluebottle.clients

from token_auth.auth import booking
from token_auth.exceptions import TokenAuthenticationError
from token_auth.views import get_auth, SSORedirectView, TokenLoginView


class MockBookingProperties(object):
    TOKEN_AUTH_BACKEND = 'token_auth.auth.booking.TokenAuthentication'
    TOKEN_AUTH = {
        'aes_key': 'test',
        'hmac_key': 'test',
        'token_expiration': datetime.now() + timedelta(hours=1)
    }


class MockIncorrectProperties(object):
    TOKEN_AUTH_BACKEND = 'non-existing-module.non-existing-class'


class MockDummyProperties(object):
    TOKEN_AUTH_BACKEND = 'token_auth.tests.test_views.DummyAuthentication'


class DummyUser(object):
    def get_jwt_token(self):
        return 'test-token'


class DummyAuthentication(object):
    def __init__(self, request, **kwargs):
        self.request = request

    def sso_url(self):
        return 'http://example.com/sso'

    def authenticate(self):
        if getattr(self.request, 'fails', False):
            raise TokenAuthenticationError('test message')

        return DummyUser(), True


class ConfigureAuthenticationClassTestCase(TestCase):
    """
    Tests the configuration of the authentication backend
    """
    @mock.patch.object(bluebottle.clients, 'properties', MockBookingProperties())
    def test_booking_class(self):
        request = RequestFactory().get('/api/sso/redirect')
        auth = get_auth(request, token='test-token')
        self.assertTrue(isinstance(auth, booking.TokenAuthentication))
        self.assertEqual(auth.args['token'], 'test-token')

    @mock.patch.object(bluebottle.clients, 'properties', MockIncorrectProperties())
    def test_incorrect_class(self):
        request = RequestFactory().get('/api/sso/redirect')
        self.assertRaises(
            ImproperlyConfigured,
            get_auth,
            request
        )


class RedirectViewTestCase(TestCase):
    def setUp(self):
        self.view = SSORedirectView()
        self.factory = RequestFactory()

    @mock.patch.object(bluebottle.clients, 'properties', MockDummyProperties())
    def test_get(self):
        response = self.view.get(self.factory.get('/api/sso/redirect'))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['sso-url'], 'http://example.com/sso')


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.view = TokenLoginView()
        self.factory = RequestFactory()

    @mock.patch.object(bluebottle.clients, 'properties', MockDummyProperties())
    def test_get(self):
        response = self.view.get(self.factory.get('/api/sso/authenticate'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/go/login-with/{}'.format(DummyUser().get_jwt_token())
        )

    @mock.patch.object(bluebottle.clients, 'properties', MockDummyProperties())
    def test_get_link(self):
        response = self.view.get(self.factory.get('/api/sso/authenticate'), link='/test')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/go/login-with/{}?%2Ftest'.format(DummyUser().get_jwt_token())
        )

    @mock.patch.object(bluebottle.clients, 'properties', MockDummyProperties())
    def test_get_authentication_failed(self):
        request = self.factory.get('/api/sso/authenticate')
        request.fails = True

        response = self.view.get(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], "/token/error?message='test%20message'"
        )
