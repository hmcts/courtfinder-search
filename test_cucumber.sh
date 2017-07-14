#!/bin/bash
set -e

APP_HOST=${APP_HOST:-http://localhost:8000/}
until curl -s -f $APP_HOST > /dev/null; do
  >&2 echo "Waiting for courtfinder"
  sleep 1
done

pushd cucumber
bundle exec cucumber features/navigation.feature
popd
