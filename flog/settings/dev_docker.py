# -*- coding: utf-8 -*-
__author__ = 'lundberg'

"""Development settings and globals."""

from flog.settings.dev import *


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'flog',
        'USER': 'flog',
        'PASSWORD': 'docker',
        'HOST': 'flog-db',
        'PORT': '5432'
    }
}
########## END DATABASE CONFIGURATION
