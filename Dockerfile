FROM debian:stable
MAINTAINER Johan Lundberg "lundberg@sunet.se"

COPY . /opt/flog/
RUN /opt/flog/docker/setup.sh
RUN /opt/flog/docker/build.sh
COPY docker/daily_eduroam.sh /usr/local/bin/daily_eduroam
COPY docker/daily_sso.sh /usr/local/bin/daily_sso
COPY docker/start.sh /start.sh
EXPOSE 8000
CMD ["/bin/sh", "-e", "/start.sh"]
