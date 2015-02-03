#!/bin/sh

/etc/init.d/postgresql start
cd /srv/search/courtfinder
python manage.py migrate
python manage.py populate-db

