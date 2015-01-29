#!/bin/sh

/etc/init.d/postgresql start
/usr/bin/psql -c 'CREATE ROLE courtfinder_search LOGIN SUPERUSER INHERIT CREATEDB CREATEROLE REPLICATION;' -U postgres
/usr/bin/psql -c 'CREATE DATABASE "courtfinder_search";' -U postgres
/usr/bin/psql -c "ALTER USER courtfinder_search WITH PASSWORD '123456';" -U postgres
PGPASSWORD=123456 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION postgis;' -U courtfinder_search
PGPASSWORD=123456 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION postgis_topology;' -U courtfinder_search

