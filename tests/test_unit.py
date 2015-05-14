import base64
import hashlib
import hmac
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from Crypto import Random
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection

from token_auth.auth import BookingTokenAuthentication, TokenAuthenticationError
from token_auth.models import CheckedToken
from .factories import CheckedTokenFactory
from token_auth.utils import get_token_settings


class TestBookingTokenAuthentication(TestCase):
    """
    Tests the Booking token authentication backend.
    """
    @override_settings(
        TOKEN_AUTH = {
            'token_expiration': 600,
            'hmac_key': 'bbbbbbbbbbbbbbbb',
            'aes_key': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        }
    )
    def setUp(self):
        # import ipdb; ipdb.set_trace()
        self.auth_backend = BookingTokenAuthentication()
        self.checked_token = CheckedTokenFactory.create()
        self.data = 'time=2013-12-23 17:51:15|username=johndoe|name=John Doe' \
                    '|email=john.doe@booking.com'

        # To keep things easy, let's just change the valid token to put some Xs
        # on it at the beginning of each of those lines.
        token = 'XbaTf5AVWkpkiACH6nNZZUVzZR0rye7rbiqrm3Qrgph5Sn3EwsFERytBwoj' \
                'XaqSdISPvvc7aefusFmHDXAJbwLvCJ3N73x4whT7XPiJz7kfrFKYal6WlD8' \
                'Xu5JZgVTmV5hdywGQkPMFT1Z7m4z1ga6Oud2KoQNhrf5cKzQ5CSdTojZmZ0' \
                'XT24jBuwm5YUqFbvwTBxg=='
        self.corrupt_token = token

        # Get the new security keys to use it around in the tests.
        self.hmac_key = get_token_settings('hmac_key')
        self.aes_key = get_token_settings('aes_key')

    def _encode_message(self, message):
        """
        Helper method for unit tests which returns an encoded version of the
        message passed as an argument.

        It returns a tuple containing a string formed by two elements:

        1. A string formed by the initialization vector and the AES-128
        encrypted message.
        2. The HMAC-SHA1 hash of that string.
        """
        pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(
            AES.block_size - len(s) % AES.block_size)
        init_vector = Random.new().read(AES.block_size)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, init_vector)
        padded_message = pad(message)
        aes_message = init_vector + cipher.encrypt(padded_message)
        hmac_digest = hmac.new(self.hmac_key, aes_message, hashlib.sha1)

        return aes_message, hmac_digest

    def test_check_hmac_signature_ok(self):
        """
        Tests that the method to check up HMAC signature of the token message
        returns True when it is a valid signature.
        """
        message = base64.urlsafe_b64decode(self.checked_token.token)
        self.assertTrue(self.auth_backend.check_hmac_signature(message))

    def test_check_hmac_signature_wrong(self):
        """
        Tests the method to check up HMAC signature when the token is corrupted
        and the signatures is not valid.
        """
        message = base64.b64decode(self.corrupt_token)

        self.assertFalse(self.auth_backend.check_hmac_signature(message))

    def test_decrypts_message(self):
        """
        Tests the method to decrypt the AES encoded message.
        """
        aes_message, hmac_digest = self._encode_message(self.data)
        message = self.auth_backend.decrypt_message(aes_message + hmac_digest.digest())
        unpad = lambda s: s[0:-ord(s[-1])]

        self.assertEqual(unpad(message), self.data)

    def test_get_login_data(self):
        """
        Tests the method to split the login message data into a 4-field tuple.
        """
        login_data = self.auth_backend.get_login_data(self.data)

        self.assertTupleEqual(
            login_data,
            (
                '2013-12-23 17:51:15',
                'johndoe',
                'John Doe',
                'john.doe@booking.com'
            ))

    def test_check_timestamp_valid_token(self):
        """
        Tests the method to check the login message timestamp when a good
        token is received.
        """
        login_time = datetime.now() - timedelta(seconds=10)
        self.assertTrue(self.auth_backend.check_timestamp(login_time))

    def test_check_timestamp_timedout_token(self):
        """
        Tests the method to check the login message timestamp when a wrong
        timestamp is given.
        """
        login_time = datetime.now() - timedelta(
            days=self.auth_backend.expiration_date + 1)
        self.assertFalse(self.auth_backend.check_timestamp(login_time))

    def test_authenticate_fail_no_token(self):
        """
        Tests that ``authenticate`` method raises an exception when no token
        is provided.
        """
        self.assertRaisesMessage(
            TokenAuthenticationError,
            'No token provided',
            self.auth_backend.authenticate)

    def test_authenticate_fail_token_used(self):
        """
        Tests that ``authenticate`` method raises an exception when a used
        token is provided.
        """
        self.assertRaisesMessage(
            TokenAuthenticationError,
            'Token was already used and is not valid',
            self.auth_backend.authenticate,
            self.checked_token.token)

    def test_authenticate_fail_corrupted_token(self):
        """
        Tests that ``authenticate`` method raises an exception when a corrupt
        token is received (HMAC-SHA1 checking).
        """
        self.assertRaisesMessage(
            TokenAuthenticationError,
            'HMAC authentication failed',
            self.auth_backend.authenticate,
            self.corrupt_token)

    def test_authenticate_fail_invalid_login_data(self):
        """
        Tests that ``authenticate`` method raises an exception when a valid
        token was received but it didn't contained valid authentication data,
        so the message contained in the token was not as expected.
        """
        message = 'xxxx=2013-12-18 11:51:15|xxxxxxxx=johndoe|xxxx=John Doe|' \
                  'xxxxx=john.doe@booking.com'
        aes_message, hmac_digest = self._encode_message(message)
        token = base64.urlsafe_b64encode(aes_message + hmac_digest.digest())

        self.assertRaisesMessage(
            TokenAuthenticationError,
            'Message does not contain valid login data',
            self.auth_backend.authenticate,
            token)

    def test_authenticate_fail_token_expired(self):
        """
        Tests that ``authenticate`` method raises an exception when the token
        expired.
        """
        # Set up a token with an old date (year 2012).
        message = 'time=2012-12-18 11:51:15|username=johndoe|name=John Doe|' \
                  'email=john.doe@booking.com'
        aes_message, hmac_digest = self._encode_message(message)
        token = base64.urlsafe_b64encode(aes_message + hmac_digest.digest())

        self.assertRaisesMessage(
            TokenAuthenticationError,
            'Authentication token expired',
            self.auth_backend.authenticate,
            token)

    def test_authenticate_successful_login(self):
        """
        Tests ``authenticate`` method when it performs a successful login.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = 'time={0}|username=johndoe|name=John Doe|' \
                  'email=john.doe@booking.com'.format(timestamp)
        aes_message, hmac_digest = self._encode_message(message)
        token = base64.urlsafe_b64encode(aes_message + hmac_digest.digest())

        user, created = self.auth_backend.authenticate(token=token)

        # Check created user data.
        self.assertEqual(user.username, 'johndoe')
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.primary_language, settings.LANGUAGE_CODE)

        # Check `CheckedToken` related object.
        checked_token = CheckedToken.objects.latest('pk')
        self.assertEqual(checked_token.token, token)
        self.assertEqual(checked_token.user, user)
        #                  timestamp)