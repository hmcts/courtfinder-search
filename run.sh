#!/bin/bash
cd /srv/search/courtfinder
if [ -e "/tmp/postgres_setup" ]; then
  echo 'Set up'
else
  bash /setup_postgresql.sh
  touch /tmp/postgres_setup
fi
# python manage.py migrate
# python manage.py populate-db
/usr/local/bin/uwsgi --ini /srv/search/uwsgi.conf