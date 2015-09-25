#!/bin/sh
EXPORT PGPASSWORD=C1cwG3P7n2

/usr/bin/psql -c 'DROP DATABASE IF EXISTS "courtfinder_production;' -h $DB_HOST -U courtfinder
/usr/bin/psql -c 'DROP DATABASE IF EXISTS "courtfinder_search;' -h $DB_HOST -U courtfinder
/usr/bin/psql -c 'CREATE DATABASE IF NOT EXISTS "courtfinder_production" WITH OWNER courtfinder_search;' -h $DB_HOST -U courtfinder
/usr/bin/psql -c 'CREATE DATABASE IF NOT EXISTS "courtfinder_search" WITH OWNER courtfinder_search;' -h $DB_HOST -U courtfinder
/usr/bin/psql courtfinder_search -c 'CREATE EXTENSION IF NOT EXISTS postgis;' -h $DB_HOST -U courtfinder
/usr/bin/psql courtfinder_search -c 'CREATE EXTENSION IF NOT EXISTS postgis_topology;' -h $DB_HOST -U courtfinder

# Importing database
cd /srv/search/courtfinder
python manage.py makemigrations
python manage.py migrate
python manage.py populate-db

