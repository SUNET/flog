# -*- coding: utf-8 -*-

from flog.settings.prod import *

__author__ = 'lundberg'


DEBUG = True

TEST_RUNNER = 'flog.testing.TemporaryDBTestRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'flog',
        'USER': 'flog',
        'PASSWORD': 'docker',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost',
    }
}

RAVEN_CONFIG = {
    'dsn': '',
}

LOGGING = None
