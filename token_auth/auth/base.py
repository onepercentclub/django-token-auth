import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from ..models import CheckedToken

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


class TokenAuthenticationError(Exception):
    """
    There was an error trying to authenticate with token.
    """
    def __init__(self, value=None):
        self.value = value if value else 'Error trying to authenticate by token'

    def __str__(self):
        return repr(self.value)


class BaseTokenAuthentication(object):
    """
    Base class for TokenAuthentication.
    """
    def __init__(self):
        self.settings = get_token_settings()

    def decrypt_message(self, token):
        """
        Should return an object with at least
        'timestamp'
        'email'

        data = {
            'timestamp': <timestamp>,
            'email': <email>
        }
        """
        raise NotImplemented()

    def check_timestamp(self, data):

        timestamp = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        time_limit = datetime.now() - \
                     timedelta(seconds=self.settings['expiration_date'])
        if timestamp > time_limit:
            raise TokenAuthenticationError('Authentication token expired')

    def check_token_used(self, token):
        if not token:
            raise TokenAuthenticationError(value='No token provided')
        try:
            CheckedToken.objects.get(token=token)
            raise TokenAuthenticationError(
                value='Token was already used and is not valid')
        except CheckedToken.DoesNotExist:
            # Token was not used previously. Continue with auth process.
            pass

    def set_user_data(self, user, data):
        for field in data:
            if hasattr(USER_MODEL, field):
                setattr(user, field, data[field])
        user.save()
        return user

    def authenticate(self, token):

        self.check_token_used(token)

        data = self.decrypt_message(token)

        self.check_timestamp(data)

        user, created = USER_MODEL.get_or_create(email=data['email'])
        user = self.set_user_data(user, data)

        CheckedToken.objects.create(token=token, user=user).save()

        return user, created