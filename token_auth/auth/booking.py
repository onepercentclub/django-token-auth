import base64
import hashlib
import hmac
import logging
import re
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from token_auth.auth.base import BaseTokenAuthentication

logger = logging.getLogger(__name__)

USER_MODEL = get_user_model()


def get_token_settings(key=None):
    """
    Load the properties.
    """

    properties_path = getattr(settings,
                              'TOKEN_AUTH_SETTINGS',
                              'django.conf.settings')

    parts = properties_path.split('.')
    module = '.'.join([parts[i] for i in range(0,len(parts)-1)])
    properties = parts[len(parts) - 1]

    try:
        m = __import__(module, fromlist=[''])
    except ImportError:
        raise ImproperlyConfigured(
            "Could not find module '{1}'".format(module))

    try:
        settings_path = getattr(m, properties)
    except AttributeError:
        raise ImproperlyConfigured(
            "{0} needs attribute name '{1}'".format(module, properties))
    try:
        token_auth_settings = getattr(settings_path, 'TOKEN_AUTH')
        if key:
            return token_auth_settings[key]
        return token_auth_settings
    except AttributeError:
        raise ImproperlyConfigured("TOKEN_AUTH missing in settings.")


def generate_token(email, username, first_name, last_name):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'time={0}|username={1}|name={2} {3}|' \
              'email={4}'.format(timestamp, username, first_name, last_name, email)
    aes_message, hmac_digest = _encode_message(message)
    token = base64.urlsafe_b64encode(aes_message + hmac_digest.digest())
    return token


def _encode_message(message):
    """
    Helper method which returns an encoded version of the
    message passed as an argument.

    It returns a tuple containing a string formed by two elements:

    1. A string formed by the initialization vector and the AES-128
    encrypted message.
    2. The HMAC-SHA1 hash of that string.
    """
    aes_key = get_token_settings('aes_key')
    hmac_key = get_token_settings('hmac_key')

    pad = lambda s: s + (AES.block_size - len(s) % AES.block_size) * chr(
        AES.block_size - len(s) % AES.block_size)
    init_vector = Random.new().read(AES.block_size)
    cipher = AES.new(aes_key, AES.MODE_CBC, init_vector)
    padded_message = pad(message)
    aes_message = init_vector + cipher.encrypt(padded_message)
    hmac_digest = hmac.new(hmac_key, aes_message, hashlib.sha1)

    return aes_message, hmac_digest



class TokenAuthenticationError(Exception):
    """
    There was an error trying to authenticate with token.
    """
    def __init__(self, value=None):
        self.value = value if value else 'Error trying to authenticate by token'

    def __str__(self):
        return repr(self.value)


class TokenAuthentication(BaseTokenAuthentication):
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
    def check_hmac_signature(self, message):
        """
        Checks the HMAC-SHA1 signature of the message.
        """
        data = message[:-20]
        checksum = message[-20:]
        hmac_data = hmac.new(self.settings['hmac_key'], data, hashlib.sha1)

        return True if hmac_data.digest() == checksum else False


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

    def decrypt_message(self, token=None):
        """
        Decrypts the AES encoded message.
        """
        token = str(token)
        message = base64.urlsafe_b64decode(token)

        # Check that the message is valid (HMAC-SHA1 checking).
        if not self.check_hmac_signature(message):
            raise TokenAuthenticationError('HMAC authentication failed')

        init_vector = token[:16]
        enc_message = token[16:-20]

        aes = AES.new(self.settings['aes_key'], AES.MODE_CBC, init_vector)
        message = aes.decrypt(enc_message)


        # Get the login data in an easy-to-use tuple.
        try:
            login_data = self.get_login_data(message)
        except AttributeError:
            # Regex failed, so data was not valid.
            raise TokenAuthenticationError('Message does not contain valid login data')

        name = login_data[2].strip()
        first_name = name.split(' ').pop(0)
        parts = name.split(' ')
        parts.pop(0)
        last_name = " ".join(parts)

        data = {
            'timestamp': login_data[0],
            'email': login_data[3].strip(),
            'first_name': first_name,
            'last_name': last_name
        }

        return data
