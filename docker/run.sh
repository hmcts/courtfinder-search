#!/bin/bash -e

echo 'Starting PostgreSQL server service'
sudo /etc/init.d/postgresql start
uwsgi --ini /srv/search/uwsgi.conf
