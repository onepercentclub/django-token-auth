#!/usr/bin/env python
import sys

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        USER_AUTH_MODEL='auth.User',
        SOUTH_TESTS_MIGRATE = False,
        USE_TZ=True,
        INSTALLED_APPS=(
            'south',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django_nose',
            'factory',
            'token_auth'
        ),
        MIDDLEWARE_CLASSES=()
    )

from django_nose import NoseTestSuiteRunner

def runtests(*test_labels):
    runner = NoseTestSuiteRunner(verbosity=3, interactive=True)
    failures = runner.run_tests(test_labels)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])

