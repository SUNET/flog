# -*- coding: utf-8 -*-
__author__ = 'lundberg'

"""Development settings and globals."""

from dev import *


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'flog',
        'USER': 'flog',
        'PASSWORD': 'docker',
        'HOST': 'db.flog.docker',
        'PORT': '5432'
    }
}
########## END DATABASE CONFIGURATION
