import os

from datetime import datetime, timedelta
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto import Random

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.contrib.sites.models import Site
from django.utils import translation


def get_token_settings(key=None):
    """
    Load the properties.
    """

    properties_path = getattr(settings, 'TOKEN_AUTH_SETTINGS', 'django.conf.settings')

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
