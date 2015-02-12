# FROM ubuntu:14.04
FROM phusion/baseimage:0.9.12

RUN apt-get update
RUN apt-get install -y postgresql-client-9.3 postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib-9.3 postgis postgresql-9.3-postgis-2.1 python-pip python-dev wget npm ruby nodejs-legacy
RUN pip install uWSGI==2.0.8

ADD /docker/. /
RUN mv /search /etc/sudoers.d/search
RUN chmod 755 /run.sh

RUN mv /pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
RUN bash /setup_postgresql.sh

RUN useradd -m -d /srv/search search

ADD ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD . /srv/search
RUN rm -rf /srv/search/.git
RUN bash /setup_npm.sh
RUN chown -R search: /srv/search

RUN wget https://courttribunalfinder.service.gov.uk/courts.json -O /srv/search/data/courts.json

WORKDIR /srv/search
RUN bash /setup_search.sh
RUN gulp

RUN update-rc.d postgresql enable
RUN chown -R search:search /srv/logs

USER search

EXPOSE 8000

USER root