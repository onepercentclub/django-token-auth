#!/usr/bin/env python

import os
import setuptools
import token_auth

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name="django-token-auth",
    version=token_auth.__version__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    license='BSD',
    description='Token Authentication for Bluebottle',
    long_description=README,
    url="http://onepercentclub.com",
    author="1%Club Developers",
    author_email="devteam@onepercentclub.com",
    install_requires=[
        'Django>=1.6.8',
        'python-saml==2.1.4'
    ],
    tests_require={
        'factory-boy>=2.6.0',
        'bunch==1.0.1',
        'django-nose>=1.4',
        'django-setuptest>=0.1.4',
        'mock>=1.0.1',
        'djangorestframework>=2.3.14'
    },
    test_suite = "token_auth.runtests.runtests"
)

