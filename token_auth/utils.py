from django.conf import settings
from django.utils.module_loading import import_by_path

from django.core.exceptions import ImproperlyConfigured


def get_settings():
    properties_path = getattr(settings,
                              'TOKEN_AUTH_SETTINGS',
                              'django.conf.settings')

    try:
        properties = import_by_path(properties_path)
    except ImportError, e:
        raise ImproperlyConfigured(e)

    try:
        return properties.TOKEN_AUTH
    except AttributeError:
        raise ImproperlyConfigured(
            'Missing TOKEN_AUTH attribute in {}'.format(properties_path)
        )
