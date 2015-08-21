import logging
import urllib

from django.contrib.auth import get_user_model
from token_auth.utils import get_settings

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

    def sso_url(self, target_url=None):
        url = self.settings['sso_url']
        if target_url:
            url += '?{}'.format(urllib.urlencode({'url': target_url}))

        return url

    @property
    def target_url(self):
        return None

    def authenticate_request(self):
        """
        Authenticate the request. Should return a dict containing data
        representing the authenticated user.

        Typically it should at least have an <email>.
        {'email': <email>}
        """
        raise NotImplemented()

    def set_user_data(self, user, data):
        """
        Set al user data that we got from the SSO service and store it
        on the user.
        """
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.save()
        return user

    def get_or_create_user(self, data):
        """
        Get or create the user.
        """
        return USER_MODEL.objects.get_or_create(email=data['email'])

    def finalize(self, user, data):
        """
        Finalize the request. Used for example to store used tokens,
        to prevent replay attacks
        """
        pass

    def process_logout(self):
        """
        Log out
        """
        pass

    def get_metadata(self):
        metadata = "<sso-url>{0}</sso-url>".format(self.sso_url())
        return metadata

    def authenticate(self):
        data = self.authenticate_request()

        user, created = self.get_or_create_user(data)
        user.is_active = True
        user = self.set_user_data(user, data)

        self.finalize(user, data)

        return user, created
