#!/usr/bin/env python
import os
import sys
from django.core.exceptions import ImproperlyConfigured

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flog.settings")

    from django.core.management import execute_from_command_line
    try:
        execute_from_command_line(sys.argv)
    except ImproperlyConfigured as e:
        print e
        print 'Maybe you forgot to use manage.py [command] --settings=flog.settings.dev|prod'
