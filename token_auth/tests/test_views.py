import urllib
from mock import patch

from django.test import TestCase, RequestFactory
from django.core.exceptions import ImproperlyConfigured

from token_auth.auth import booking, base
from token_auth.exceptions import TokenAuthenticationError
from token_auth.views import get_auth, TokenRedirectView, TokenLoginView


DUMMY_AUTH = {'backend': 'token_auth.tests.test_views.DummyAuthentication'}


class DummyUser(object):
    def get_jwt_token(self):
        return 'test-token'


class DummyAuthentication(base.BaseTokenAuthentication):
    def authenticate(self):
        if getattr(self.request, 'fails', False):
            raise TokenAuthenticationError('test message')

        return DummyUser(), True


class ConfigureAuthenticationClassTestCase(TestCase):
    """
    Tests the configuration of the authentication backend
    """
    def test_booking_class(self):
        with self.settings(TOKEN_AUTH={'backend': 'token_auth.auth.booking.TokenAuthentication'}):
            request = RequestFactory().get('/api/sso/redirect')
            auth = get_auth(request, token='test-token')
            self.assertTrue(isinstance(auth, booking.TokenAuthentication))
            self.assertEqual(auth.args['token'], 'test-token')

    def test_incorrect_class(self):
        with self.settings(TOKEN_AUTH={'backend': 'non-existing-module.non-existing-class'}):
            request = RequestFactory().get('/api/sso/redirect')
            self.assertRaises(
                ImproperlyConfigured,
                get_auth,
                request
            )


class RedirectViewTestCase(TestCase):
    def setUp(self):
        self.view = TokenRedirectView()
        self.factory = RequestFactory()

    @patch.object(DummyAuthentication, 'sso_url', return_value='http://example.com/sso')
    def test_get(self, sso_url):
        with self.settings(TOKEN_AUTH=DUMMY_AUTH):
            response = self.view.get(self.factory.get('/api/sso/redirect'))
            expected_url = 'http://example.com/sso'

            sso_url.assert_called_once_with(target_url=None)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, expected_url)

    @patch.object(DummyAuthentication, 'sso_url', return_value='http://example.com/sso')
    def test_get_custom_target(self, sso_url):
        with self.settings(TOKEN_AUTH=DUMMY_AUTH):
            response = self.view.get(
                self.factory.get('/api/sso/redirect?' + urllib.urlencode({'url': '/test/'}))
            )

            sso_url.assert_called_once_with(target_url='/test/')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, 'http://example.com/sso')


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.view = TokenLoginView()
        self.factory = RequestFactory()

    def test_get(self):
        with self.settings(TOKEN_AUTH={'backend': 'token_auth.tests.test_views.DummyAuthentication'}):
            response = self.view.get(self.factory.get('/api/sso/authenticate'))

            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response['Location'], '/login-with/{}'.format(DummyUser().get_jwt_token())
            )

    def test_get_link(self):
        with self.settings(TOKEN_AUTH={'backend': 'token_auth.tests.test_views.DummyAuthentication'}):
            response = self.view.get(self.factory.get('/api/sso/authenticate'), link='/test')

            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response['Location'],
                '/login-with/{}?next=%2Ftest'.format(DummyUser().get_jwt_token())
            )

    def test_get_authentication_failed(self):
        with self.settings(TOKEN_AUTH={'backend': 'token_auth.tests.test_views.DummyAuthentication'}):
            request = self.factory.get('/api/sso/authenticate')
            request.fails = True

            response = self.view.get(request)

            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response['Location'],
                "/token/error?message='test%20message'"
            )
