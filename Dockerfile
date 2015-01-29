FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y postgresql-client-9.3 postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib-9.3 postgis postgresql-9.3-postgis-2.1 varnish

ADD docker/* /
RUN mv /pg_hba.conf /etc/postgresql/9.3/main/pg_hba.conf
RUN bash /setup_postgresql.sh

EXPOSE 6081