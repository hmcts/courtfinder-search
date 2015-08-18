#!/bin/bash -e

/etc/init.d/postgresql start
cd /srv/search
python manage.py migrate
python manage.py populate-db