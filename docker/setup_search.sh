#!/bin/bash -e

cd /srv/search/courtfinder
python manage.py migrate
python manage.py populate-db