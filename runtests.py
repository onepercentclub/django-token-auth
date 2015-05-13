#!/usr/bin/env python
import sys

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        USER_AUTH_MODEL='auth.User',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'tests',
            'django_nose',
            'factory'
        ],
        MIDDLEWARE_CLASSES=()
    )

from django_nose import NoseTestSuiteRunner

def runtests(*test_labels):
    # django.setup()
    runner = NoseTestSuiteRunner(verbosity=1, interactive=True)
    failures = runner.run_tests(test_labels)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])

