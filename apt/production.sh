#!/usr/bin/env bash

$(dirname $0)/base.sh

apt-get install --fix-missing -y \
        npm \
        nodejs
