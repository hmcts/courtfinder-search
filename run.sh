#!/bin/bash
cd /srv/search/

case ${DOCKER_STATE} in
migrate)
    echo "Docker state set to ${DOCKER_STATE}, running migrate commands..."
    python courtfinder/manage.py migrate
    python courtfinder/manage.py collectstatic --noinput
    ;;
create)
    echo "Docker state set to ${DOCKER_STATE}, running create commands..."
    python courtfinder/manage.py makemigrations
    python courtfinder/manage.py collectstatic --noinput
    python courtfinder/manage.py migrate
    ;;
*)
    echo "Docker state set to ${DOCKER_STATE}... no commands found."
esac

echo "Starting server..."
sudo sysctl -w net.core.somaxconn=500
/usr/local/bin/uwsgi --ini /srv/search/uwsgi.conf --listen 500
