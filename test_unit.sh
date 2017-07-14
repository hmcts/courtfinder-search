#!/bin/bash
set -e

until psql postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST/$DB_NAME -c '\l' >/dev/null 2>&1; do
  >&2 echo "Waiting for Postgres"
  sleep 1
done

pushd courtfinder
python manage.py test -v 2
popd
