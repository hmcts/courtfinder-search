FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y postgresql-client-9.3 postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib-9.3 postgis postgresql-9.3-postgis-2.1 python-pip python-dev

ADD ./docker/pg_hba.conf /pg_hba.conf
ADD ./docker/setup_postgresql.sh /setup_postgresql.sh
ADD ./docker/run.sh /run.sh
RUN chmod 755 /run.sh

RUN mv /pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
RUN bash /setup_postgresql.sh

RUN useradd -m -d /srv/search search

ADD . /srv/search
RUN rm -rf /srv/search/.git
RUN chown -R search: /srv/search
RUN pip install -r /srv/search/requirements.txt


USER search
WORKDIR /srv/search

EXPOSE 8080