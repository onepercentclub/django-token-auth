import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from bluebottle import clients

from token_auth.exceptions import TokenAuthenticationError
from token_auth.utils import get_settings
from ..models import CheckedToken

logger = logging.getLogger(__name__)

USER_MODEL = get_user_model()


class BaseTokenAuthentication(object):
    """
    Base class for TokenAuthentication.
    """
    def __init__(self, request, **kwargs):
        self.args = kwargs

        self.settings = get_settings()

    def decrypt_message(self):
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
            timedelta(seconds=self.settings['token_expiration'])
        if timestamp < time_limit:
            raise TokenAuthenticationError('Authentication token expired')

        return timestamp

    def check_token_used(self):
        if not self.args.get('token'):
            raise TokenAuthenticationError(value='No token provided')
        try:
            CheckedToken.objects.get(token=self.args['token'])
            raise TokenAuthenticationError(
                value='Token was already used and is not valid')
        except CheckedToken.DoesNotExist:
            # Token was not used previously. Continue with auth process.
            pass

    def set_user_data(self, user, data):
        for field in data:
            if hasattr(user, field):
                setattr(user, field, data[field])
        user.save()
        return user

    def authenticate(self):
        self.check_token_used()

        data = self.decrypt_message()

        timestamp = self.check_timestamp(data)

        user, created = USER_MODEL.objects.get_or_create(email=data['email'])

        user = self.set_user_data(user, data)

        CheckedToken.objects.create(token=self.args['token'], user=user, timestamp=timestamp).save()

        return user, created
