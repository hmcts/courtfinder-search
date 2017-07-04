#!/bin/bash -e
[ -e /usr/bin/node ] || ln -s /usr/bin/nodejs /usr/bin/node
npm install
npm install gulp -g
gem install sass
