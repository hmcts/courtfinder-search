#!/bin/bash
cd /srv/search/

case ${DOCKER_STATE} in
migrate)
    echo "Docker state set to ${DOCKER_STATE}, running migrate commands..."
    python manage.py migrate
    ;;
seed)
    echo "Docker state set to ${DOCKER_STATE}, running seed commands..."
    python manage.py populate-db
    ;;
create)
    echo "Docker state set to ${DOCKER_STATE}, running create commands..."
    python manage.py makemigrations
    python manage.py migrate
    python manage.py populate-db
    ;;
*)
    echo "Docker state set to ${DOCKER_STATE}... no commands found."
esac

echo "Starting server..."
/usr/local/bin/uwsgi --ini /srv/search/uwsgi.conf
