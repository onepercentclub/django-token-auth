#!/usr/bin/env python
import os
import sys

import coverage


def runtests(args=None):
    test_dir = os.path.dirname(__file__)
    sys.path.insert(0, test_dir)

    import django
    from django.test.utils import get_runner
    from django.conf import settings

    settings.configure(
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3'}},
        USER_AUTH_MODEL='tests.User',
        USE_TZ=True,
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django_nose',
            'factory',
            'token_auth',
            'token_auth.tests'
        ),
        MIDDLEWARE_CLASSES=()
    )

    django.setup()

    cov = coverage.Coverage()
    cov.start()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    args = args or ['.']
    failures = test_runner.run_tests(args)

    cov.stop()
    cov.save()
    if os.getenv('HTML_REPORT'):
        cov.html_report()

    sys.exit(failures)


if __name__ == '__main__':
    runtests(sys.argv[1:])
