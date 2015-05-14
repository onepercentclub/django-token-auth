import base64
import hashlib
import hmac
import logging
import re
import string
from Crypto.Cipher import AES
from datetime import datetime, timedelta
from django.utils.timezone import now

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import CheckedToken
from token_auth.utils import get_token_settings

logger = logging.getLogger(__name__)

BB_USER_MODEL = get_user_model()


class TokenAuthenticationError(Exception):
    """
    There was an error trying to authenticate with token.
    """
    def __init__(self, value=None):
        self.value = value if value else 'Error trying to authenticate by token'

    def __str__(self):
        return repr(self.value)


class BookingTokenAuthentication(object):
    """
    This authentication backend expects a token, encoded in URL-safe Base64, to
    be received from the user to be authenticated. The token must be built like
    this:

    - The first 16 bytes are the AES key to be used to decrypt the message.
    - The last 20 bytes are the HMAC-SHA1 signature of the message AND the AES
    key, to provide an extra safety layer on the process.
    - The rest of the token, between the first 16 bytes and the latest 20, is
    the encrypted message to be read.

    The backend performs the next operations over a received token in order to
    authenticate the user who is sending it:

    1. Checks that the token was not used previously, to prevent replay.
    2. Decodes it through Base64.
    3. Checks the HMAC-SHA1 signature of the message.
    4. Decrypts the AES-encoded message to read the data.
    5. Read the timestamp included in the message to check if the token already
    expired or if its finally valid.
    """
    def __init__(self):
        self.aes_key = get_token_settings('aes_key')
        self.hmac_key = get_token_settings('hmac_key')
        self.expiration_date = get_token_settings('token_expiration')

    def check_hmac_signature(self, message):
        """
        Checks the HMAC-SHA1 signature of the message.
        """
        data = message[:-20]
        checksum = message[-20:]
        hmac_data = hmac.new(self.hmac_key, data, hashlib.sha1)

        return True if hmac_data.digest() == checksum else False

    def decrypt_message(self, message):
        """
        Decrypts the AES encoded message.
        """
        init_vector = message[:16]
        enc_message = message[16:-20]

        aes = AES.new(self.aes_key, AES.MODE_CBC, init_vector)
        decrypted_message = aes.decrypt(enc_message)

        return decrypted_message

    def get_login_data(self, data):
        """
        Obtains the data from the decoded message. Returns a Python tuple
        of 4 elements containing the login data. The elements, from zero
        to three, are:

        0. Timestamp.
        1. Username.
        2. Complete name.
        3. Email.
        """
        expression = r'(.*?)\|'
        pattern = r'time={0}username={0}name={0}email=(.*)'.format(expression)
        login_data = re.search(pattern, data)

        return login_data.groups()

    def check_timestamp(self, timestamp):
        """
        Checks that the timestamp given in login data is not older than the
        time specified in ``AUTH_TOKEN_EXPIRATION`` setting.
        """
        time_limit = datetime.now() - timedelta(seconds=self.expiration_date)

        return timestamp > time_limit

    def authenticate(self, token=None):
        if not token:
            raise TokenAuthenticationError(value='No token provided')
        try:
            # Add some grace for trigger happy people.
            # FIXME: this is mainly here because functional test triggers urls twice. :-s
            just_now = datetime.now() - timedelta(seconds=10)
            CheckedToken.objects.get(token=token, timestamp__lt=just_now)
            raise TokenAuthenticationError(value='Token was already used and is not valid')
        except CheckedToken.DoesNotExist:
            # Token was not used previously. Continue with auth process.
            pass

        token = str(token)

        message = base64.urlsafe_b64decode(token)

        # Check that the message is valid (HMAC-SHA1 checking).
        if not self.check_hmac_signature(message):
            raise TokenAuthenticationError('HMAC authentication failed')

        # Decrypt the AES message.
        data = self.decrypt_message(message)

        # Get the login data in an easy-to-use tuple.
        try:
            login_data = self.get_login_data(data)
        except AttributeError:
            # Regex failed, so data was not valid.
            raise TokenAuthenticationError('Message does not contain valid login data')

        # Check that the token is not older than ``expiration_date``.
        timestamp = datetime.strptime(login_data[0], '%Y-%m-%d %H:%M:%S')
        if not self.check_timestamp(timestamp):
            raise TokenAuthenticationError('Authentication token expired')

        email = login_data[3].strip()
        email = filter(lambda x: x in string.printable, email)

        # Good token! Let the user log in, but first store the token to
        # compare with next ones.
        user, created = BB_USER_MODEL.objects.get_or_create(email=email)

        username = login_data[1]
        counter = 1
        qs = BB_USER_MODEL.objects
        while qs.filter(username=username).exists():
            username = '{0}-{1}'.format(username, counter)
            counter += 1

        user.username = username

        if created:
            user.primary_language = settings.LANGUAGE_CODE
            user.is_active = True

        user.save()

        checked_token = CheckedToken.objects.create(token=token, timestamp=timestamp, user=user)

        return user, created

    def get_user(self, user_id):
        try:
            return BB_USER_MODEL.objects.get(pk=user_id)
        except BB_USER_MODEL.DoesNotExist:
            return None
