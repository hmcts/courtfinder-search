FROM ubuntu:14.04

RUN apt-get clean && apt-get update
RUN apt-get install --fix-missing -y postgresql-client postgresql postgresql-server-dev-all postgresql-contrib postgis postgresql-9.3-postgis-2.1 python-pip python-dev wget npm ruby nodejs-legacy
RUN pip install uWSGI==2.0.8

COPY /docker/. /
RUN mv /search /etc/sudoers.d/search; chmod 755 /run.sh; mv /pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf; mkdir -p /srv/node_files
COPY ./package.json /srv/node_files/package.json
RUN bash /setup_postgresql.sh; bash /setup_npm.sh; useradd -m -d /srv/search search

COPY ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN sudo -u search mkdir -p /srv/search

COPY . /srv/search

RUN wget https://courttribunalfinder.service.gov.uk/courts.json -O /srv/search/data/courts.json

WORKDIR /srv/search
RUN bash /setup_search.sh
RUN mv /srv/node_files/node_modules /srv/search/
RUN gulp

RUN update-rc.d postgresql enable
RUN chown -R search:search /srv/logs
RUN chown -R search: /srv/search

USER search