import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model

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
        self.request = request

        self.settings = get_settings()

    def sso_url(self):
        return self.settings['sso_url']

    def authenticate_request(self):
        """
        Authenticate the request. Should return a dict containing data representing
        the authenticated user.
        """
        raise NotImplemented()

    def set_user_data(self, user, data):
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.save()

        return user

    def get_or_create_user(self, data):
        return USER_MODEL.objects.get_or_create(email=data['email'])
    def finalize(self, user, data):
        """ Finalize the request. Used for example to store used tokens, to prevent
        replay attacks
        """
        pass

    def authenticate(self):
        data = self.authenticate_request()

        data = self.decrypt_message()

        user, created = self.get_or_create_user(data)
        user.is_active = True
        user = self.set_user_data(user, data)

        self.finalize(user, data)

        return user, created
