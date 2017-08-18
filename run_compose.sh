#!/bin/bash
set -e

until psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST/$DB_NAME -c '\l' >/dev/null 2>&1; do
  >&2 echo "Waiting for Postgres"
  sleep 1
done
>&2 echo "Postgres up on postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST/$DB_NAME"

python courtfinder/manage.py makemigrations
python courtfinder/manage.py migrate
python courtfinder/manage.py populate-db --ingest
python courtfinder/manage.py runserver 0.0.0.0:8000
