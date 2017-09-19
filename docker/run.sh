#!/bin/sh

set -e
set -x

. /opt/env/bin/activate

exec start-stop-daemon --start --chdir /opt/flog/ --startas /usr/local/bin/uwsgi --name uwsgi -- --http :8000 -p 8 --master -H /opt/env --static-map /static=/opt/flog/flog/static --static-map /static=/opt/env/lib/python2.7/site-packages/django/contrib/admin/static --module flog.wsgi:application
