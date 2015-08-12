FROM ubuntu:14.04

RUN apt-get clean && apt-get update && apt-get install --fix-missing -y postgis postgresql-9.3-postgis-2.1 python-pip python-dev wget npm ruby nodejs-legacy libpq-dev libnet-amazon-s3-tools-perl
RUN pip install uWSGI==2.0.8

COPY /docker/. /
RUN mv /search /etc/sudoers.d/search; chmod 755 /run.sh; mkdir -p /srv/node_files
COPY ./package.json /srv/node_files/package.json
# RUN bash /setup_postgresql.sh;
RUN bash /setup_npm.sh; useradd -m -d /srv/search search

COPY ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN sudo -u search mkdir -p /srv/search

COPY . /srv/search

RUN wget https://courttribunalfinder.service.gov.uk/courts.json -O /srv/search/data/courts.json

WORKDIR /srv/search
RUN mv /srv/node_files/node_modules /srv/search/

WORKDIR /srv/search/courtfinder
ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production
RUN gulp
RUN /bin/bash -c python manage.py collectstatic --noinput
RUN cp -R assets /srv/search/assets

RUN mkdir -p /srv/logs; chown -R search:search /srv/logs
RUN chown -R search: /srv/search

COPY run.sh /run.sh
RUN chmod +x /run.sh

USER search

CMD ["/bin/bash", "-l", "/run.sh"]