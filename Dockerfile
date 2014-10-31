FROM ubuntu:14.04
MAINTAINER Johan Lundberg "lundberg@nordu.net"

RUN apt-get -qq update && apt-get install -y python-dev python-setuptools supervisor git-core libpq-dev
RUN easy_install pip
RUN pip install virtualenv
RUN pip install uwsgi
RUN virtualenv /opt/env/
ADD . /opt/flog/
VOLUME /opt/flog/logs/
ADD docker/supervisor.conf /opt/supervisor.conf
ADD docker/run.sh /usr/local/bin/run
RUN (cd /opt/flog/ && git remote rm origin && git remote add origin https://github.com/SUNET/flog.git)
RUN /opt/env/bin/pip install -r /opt/flog/requirements/prod.txt
RUN (cd /opt/flog && /opt/env/bin/python manage.py collectstatic --settings=flog.settings.common --noinput)
