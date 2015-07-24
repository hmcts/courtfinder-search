#!/bin/sh

/usr/bin/psql -c 'CREATE ROLE courtfinder_search LOGIN SUPERUSER INHERIT CREATEDB CREATEROLE REPLICATION;' -U postgres -h $DB_HOSTNAME
/usr/bin/psql -c 'CREATE DATABASE "courtfinder_search" WITH OWNER courtfinder;' -U postgres -h $DB_HOSTNAME
/usr/bin/psql -c "ALTER USER courtfinder WITH PASSWORD '123456';" -U postgres -h $DB_HOSTNAME
PGPASSWORD=123456 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION postgis;' -U courtfinder -h $DB_HOSTNAME
PGPASSWORD=123456 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION postgis_topology;' -U courtfinder -h $DB_HOSTNAME
