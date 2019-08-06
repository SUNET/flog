# -*- coding: utf-8 -*-
import sys

from flog.testing import PostgresqlTemporaryInstance, MemcachedTemporaryInstance
from flog.settings.prod import *

__author__ = 'lundberg'

TMP_DB = PostgresqlTemporaryInstance.get_instance()
TMP_CACHE = MemcachedTemporaryInstance.get_instance()

TEST_RUNNER = 'flog.testing.TemporaryDBTestRunner'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'flog',
        'USER': 'flog',
        'PASSWORD': 'docker',
        'HOST': 'localhost',
        'PORT': TMP_DB.port,
        'CONN_MAX_AGE': 60,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'localhost:{}'.format(TMP_CACHE.port),
    }
}

RAVEN_CONFIG = {
    'dsn': '',
}

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}
