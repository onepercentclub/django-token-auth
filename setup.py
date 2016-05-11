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
        'pycrypto>=2.6.1',
        'python-saml==2.1.7'
    ],
    tests_require={
        'django_nose>=1.4',
        'factory-boy==2.3.1',
        'django-setuptest==0.1.4',
        'mock==1.0.1',
    },
    test_suite="token_auth.runtests.runtests",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: None',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ]
)
