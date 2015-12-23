import urlparse
import os

from mock import patch
from django.test import TestCase, RequestFactory

from token_auth.exceptions import TokenAuthenticationError
from token_auth.auth.saml import SAMLAuthentication


TOKEN_AUTH_SETTINGS = {
    'backend': 'token_auth.auth.booking.SAMLAuthentication',
    'assertion_mapping': {
        'email': 'mail',
        'remote_id': 'remoteId',
        'username': 'uid'
    },
    "strict": False,
    "debug": False,
    "custom_base_path": "../../../tests/data/customPath/",
    "sp": {
        "entityId": "http://stuff.com/endpoints/metadata.php",
        "assertionConsumerService": {
            "url": "http://stuff.com/endpoints/endpoints/acs.php"
        },
        "singleLogoutService": {
            "url": "http://stuff.com/endpoints/endpoints/sls.php"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified"
    },
    "idp": {
        "entityId": "http://idp.example.com/",
        "singleSignOnService": {
            "url": "http://idp.example.com/SSOService.php"
        },
        "singleLogoutService": {
            "url": "http://idp.example.com/SingleLogoutService.php"
        },
        "x509cert": (
            "MIICgTCCAeoCCQCbOlrWDdX7FTANBgkqhkiG9w0BAQUFADCBhDELMAkGA1UEBhMCTk"
            "8xGDAWBgNVBAgTD0FuZHJlYXMgU29sYmVyZzEMMAoGA1UEBxMDRm9vMRAwDgYDVQQK"
            "EwdVTklORVRUMRgwFgYDVQQDEw9mZWlkZS5lcmxhbmcubm8xITAfBgkqhkiG9w0BCQ"
            "EWEmFuZHJlYXNAdW5pbmV0dC5ubzAeFw0wNzA2MTUxMjAxMzVaFw0wNzA4MTQxMjAx"
            "MzVaMIGEMQswCQYDVQQGEwJOTzEYMBYGA1UECBMPQW5kcmVhcyBTb2xiZXJnMQwwCg"
            "YDVQQHEwNGb28xEDAOBgNVBAoTB1VOSU5FVFQxGDAWBgNVBAMTD2ZlaWRlLmVybGFu"
            "Zy5ubzEhMB8GCSqGSIb3DQEJARYSYW5kcmVhc0B1bmluZXR0Lm5vMIGfMA0GCSqGSI"
            "b3DQEBAQUAA4GNADCBiQKBgQDivbhR7P516x/S3BqKxupQe0LONoliupiBOesCO3SH"
            "bDrl3+q9IbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHISKOtPlAeTZSnb8QAu7a"
            "RjZq3+PbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d1EDwXJW1rRXuUt4C8QID"
            "AQABMA0GCSqGSIb3DQEBBQUAA4GBACDVfp86HObqY+e8BUoWQ9+VMQx1ASDohBjwOs"
            "g2WykUqRXF+dLfcUH9dWR63CtZIKFDbStNomPnQz7nbK+onygwBspVEbnHuUihZq3Z"
            "UdmumQqCw4Uvs/1Uvq3orOo/WJVhTyvLgFVK2QarQ4/67OZfHd7R+POBXhophSMv1ZOo"
        )
    },
    "security": {
        "authnRequestsSigned": False,
        "wantAssertionsSigned": False,
        "signMetadata": False
    },
    "contactPerson": {
        "technical": {
            "givenName": "technical_name",
            "emailAddress": "technical@example.com"
        },
        "support": {
            "givenName": "support_name",
            "emailAddress": "support@example.com"
        }
    },
    "organization": {
        "en-US": {
            "name": "sp_test",
            "displayname": "SP test",
            "url": "http://sp.example.com"
        }
    }
}


class TestSAMLTokenAuthentication(TestCase):
    """
    Tests the Token Authentication backend.
    """
    def test_sso_url(self):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            request = RequestFactory().get('/sso/redirect', HTTP_HOST='www.stuff.com')
            auth_backend = SAMLAuthentication(request)

            sso_url = urlparse.urlparse(auth_backend.sso_url())
            query = urlparse.parse_qs(sso_url.query)
            self.assertEqual(
                urlparse.urlunparse((
                    sso_url.scheme, sso_url.netloc, sso_url.path, None, None, None)
                ),
                TOKEN_AUTH_SETTINGS['idp']['singleSignOnService']['url']
            )

            self.assertTrue('SAMLRequest' in query)
            self.assertEqual(query['RelayState'][0], 'http://www.stuff.com/sso/redirect')

    def test_sso_url_custom_target(self):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            request = RequestFactory().get('/sso/redirect', HTTP_HOST='www.stuff.com')
            auth_backend = SAMLAuthentication(request)

            sso_url = urlparse.urlparse(auth_backend.sso_url(target_url='/test'))
            query = urlparse.parse_qs(sso_url.query)
            self.assertEqual(
                urlparse.urlunparse((
                    sso_url.scheme, sso_url.netloc, sso_url.path, None, None, None)
                ),
                TOKEN_AUTH_SETTINGS['idp']['singleSignOnService']['url']
            )

            self.assertTrue('SAMLRequest' in query)
            self.assertEqual(query['RelayState'][0], '/test')

    def test_auth_succes(self):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            filename = os.path.join(
                os.path.dirname(__file__), 'data/valid_response.xml.base64'
            )
            with open(filename) as response_file:
                response = response_file.read()

            request = RequestFactory().post('/sso/auth', HTTP_HOST='www.stuff.com', data={'SAMLResponse': response})
            auth_backend = SAMLAuthentication(request)

            user, created = auth_backend.authenticate()

            self.assertTrue(created)

            self.assertEqual(user.username, 'smartin')
            self.assertEqual(user.email, 'smartin@yaco.es')

    def test_auth_custom_target(self):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            filename = os.path.join(
                os.path.dirname(__file__), 'data/valid_response.xml.base64'
            )
            with open(filename) as response_file:
                response = response_file.read()

            request = RequestFactory().post(
                '/sso/auth',
                HTTP_HOST='www.stuff.com',
                data={'SAMLResponse': response, 'RelayState': '/test'}
            )
            auth_backend = SAMLAuthentication(request)

            self.assertEqual(auth_backend.target_url, '/test')

    @patch('token_auth.auth.saml.logger.error')
    def test_auth_invalid(self, error):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            filename = os.path.join(
                os.path.dirname(__file__), 'data/invalid_response.xml.base64'
            )
            with open(filename) as response_file:
                response = response_file.read()

            request = RequestFactory().post(
                '/sso/auth',
                HTTP_HOST='www.stuff.com',
                data={'SAMLResponse': response}
            )
            auth_backend = SAMLAuthentication(request)

            self.assertRaises(
                TokenAuthenticationError,
                auth_backend.authenticate
            )
            error.assert_called_with((
                'Saml login error: [\'invalid_response\'], reason: '
                'Signature validation failed. SAML Response rejected'
            ))

    @patch('token_auth.auth.saml.logger.error')
    def test_auth_no_response(self, error):
        with self.settings(TOKEN_AUTH=TOKEN_AUTH_SETTINGS):
            request = RequestFactory().post('/sso/auth', HTTP_HOST='www.stuff.com')
            auth_backend = SAMLAuthentication(request)

            self.assertRaises(
                TokenAuthenticationError,
                auth_backend.authenticate
            )

            error.assert_called_with((
                'Saml login error: SAML Response not found, '
                'Only supported HTTP_POST Binding'
            ))
