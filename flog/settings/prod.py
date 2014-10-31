# -*- coding: utf-8 -*-
__author__ = 'lundberg'

"""Production settings and globals."""

from os import environ
import dotenv
from common import *

# Read .env from project root
dotenv.read_dotenv(join(SITE_ROOT, '.env'))

########## PROJECT CONFIGURATION
EDUROAM_META_DATA = environ.get('FLOG_EDUROAM_META_DATA', '')
########## PROJECT CONFIGURATION

########## ALLOWED HOSTS CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['flog.sunet.se', '127.0.0.1']
########## END ALLOWED HOST CONFIGURATION

########## SENTRY CONFIGURATION
# Set your DSN value
RAVEN_CONFIG = {
    'dsn': environ.get('FLOG_SENTRY_DSN', ''),
}
INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
########## END SENTRY CONFIGURATION

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = environ.get('FLOG_EMAIL_HOST', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = environ.get('FLOG_EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = environ.get('FLOG_EMAIL_HOST_USER', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = environ.get('FLOG_EMAIL_PORT', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': environ.get('FLOG_DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': environ.get('FLOG_DB_NAME', 'flog'),
        'USER': environ.get('FLOG_DB_USER', 'flog'),
        'PASSWORD': environ['FLOG_DB_PASSWORD'],
        'HOST': environ.get('FLOG_DB_HOST', 'localhost'),
        'PORT': environ.get('FLOG_DB_PORT', '5432')
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': environ.get('FLOG_CACHE_BACKEND', 'django.core.cache.backends.db.DatabaseCache'),
        'LOCATION': environ.get('FLOG_CACHE_LOCATION', 'flog_cache_table'),
    }
}
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 86400  # 24h
CACHE_MIDDLEWARE_KEY_PREFIX = ''
########## END CACHE CONFIGURATION

