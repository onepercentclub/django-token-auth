import logging

from django.contrib.auth import get_user_model

from token_auth.utils import get_settings

logger = logging.getLogger(__name__)


class BaseTokenAuthentication(object):
    """
    Base class for TokenAuthentication.
    """
    def __init__(self, request, **kwargs):
        self.args = kwargs
        self.request = request

        self.settings = get_settings()

    def sso_url(self, target_url=None):
        raise NotImplemented()

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

    def get_user_data(self, user, data):
        """
        Set al user data that we got from the SSO service and store it
        on the user.
        """
        return dict([(key, value) for key, value in data.items if hasattr(user, key)])

    def get_or_create_user(self, data):
        """
        Get or create the user.
        """
        user_data = self.get_user_data(data)
        return get_user_model().objects.get_or_create(
            remote_id=data['remote_id'], defaults=user_data
        )

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
        raise NotImplemented()

    def authenticate(self):
        data = self.authenticate_request()
        data['is_active'] = True

        user, created = self.get_or_create_user(data)
        self.finalize(user, data)

        return user, created
