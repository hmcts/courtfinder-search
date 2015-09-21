#!/bin/sh
/usr/bin/psql -c 'CREATE DATABASE IF NOT EXISTS "courtfinder_production" WITH OWNER courtfinder_search;' -h $DB_HOST
/usr/bin/psql -c 'CREATE DATABASE IF NOT EXISTS "courtfinder_search" WITH OWNER courtfinder_search;' -h $DB_HOST
PGPASSWORD=C1cwG3P7n2 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION IF NOT EXISTS postgis;' -h $DB_HOST
PGPASSWORD=C1cwG3P7n2 /usr/bin/psql courtfinder_search -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;' -h $DB_HOST

# Importing database
python manage.py makemigrations
python manage.py migrate
python manage.py populate-db

