FROM ubuntu:14.04
MAINTAINER Johan Lundberg "lundberg@sunet.se"

RUN apt-get -qq update && apt-get -y dist-upgrade && apt-get install -y python-dev python-setuptools git-core libpq-dev
RUN easy_install pip
RUN pip install virtualenv
RUN pip install uwsgi
RUN virtualenv /opt/env/
ADD . /opt/flog/
VOLUME /opt/flog/logs/
ADD docker/run.sh /usr/local/bin/run
ADD docker/daily_eduroam.sh /usr/local/bin/daily_eduroam
ADD docker/daily_sso.sh /usr/local/bin/daily_sso
RUN /opt/env/bin/pip install -r /opt/flog/requirements/prod.txt
RUN (cd /opt/flog && /opt/env/bin/python manage.py collectstatic --settings=flog.settings.common --noinput)
EXPOSE 8000
CMD ["/bin/sh", "-e", "/usr/local/bin/run"]
