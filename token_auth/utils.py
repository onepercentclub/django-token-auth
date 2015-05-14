
import os

from contextlib import contextmanager

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