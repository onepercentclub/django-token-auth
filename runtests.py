#!/usr/bin/env python
import sys

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        INSTALLED_APPS=[
            'django.contrib.auth',
            'tests',
            'django_nose',
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

