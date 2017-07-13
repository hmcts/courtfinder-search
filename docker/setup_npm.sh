#!/bin/bash -e
[ -e /usr/bin/node ] || ln -s /usr/bin/nodejs /usr/bin/node
npm install
gem install sass
