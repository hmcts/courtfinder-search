#!/usr/bin/env bash

$(dirname $0)/base.sh

curl -sL https://deb.nodesource.com/setup_6.x | bash -
apt install nodejs
