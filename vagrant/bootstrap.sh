#!/bin/bash

rm -f /home/vagrant/.ssh/known_hosts
ssh-keyscan -t rsa,dsa -H github.com >> /home/vagrant/.ssh/known_hosts

echo "Installing debian dependencies"
sudo apt-get clean
sudo apt-get update
# Dependencies from Dockerfile
sudo apt-get install --fix-missing -y \
  postgis \
  postgresql-9.3-postgis-2.1 \
  python-pip \
  python-dev \
  wget \
  npm \
  ruby \
  nodejs-legacy \
  libpq-dev \
  libnet-amazon-s3-tools-perl \
  git \
  build-essential \
  libssl-dev \
  libffi-dev
# Application dependencies
sudo apt-get install --fix-missing -y \
  redis-server
# Development tools
sudo apt-get install --fix-missing -y \
  htop

# Add the en_GB locale
locale -a | grep -q en_GB.utf8 || sudo locale-gen en_GB.UTF-8

echo "Setting up virtualenv"
#sudo easy_install pi#p
sudo pip install virtualenvwrapper

cd /home/vagrant/
mkdir -p .envs

grep -q "# courtfinder startup" .bashrc || cat << EOF >> .bashrc
# courtfinder startup
export WORKON_HOME=/home/vagrant/.envs
source /usr/local/bin/virtualenvwrapper.sh
workon courtfinder_search
echo -e "\\n\\n\\033[0;31mRun: ./manage.py runserver 0.0.0.0:8000\\033[0m\\n\\n"
EOF

WORKON_HOME=/home/vagrant/.envs
source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv courtfinder_search
setvirtualenvproject $VIRTUAL_ENV /courtfinder_search/
workon courtfinder_search

sudo mkdir -p /logs
sudo chown vagrant /logs

echo "Installing python dependencies"
pip install setuptools==32
pip install -r requirements.txt

echo "Setting up postgres"
sudo -u postgres bash -c "psql postgres -tAc 'SELECT 1 FROM pg_roles WHERE rolname='\''vagrant'\' | grep -q 1 || createuser --superuser vagrant"
sudo -u postgres bash -c "psql postgres -tc 'SELECT 1 FROM pg_database WHERE datname = '\''courtfinder_search'\' | grep -q 1 || createdb courtfinder_search --owner=vagrant"

cd /courtfinder_search/courtfinder/

./manage.py syncdb --noinput
./manage.py migrate --noinput
./manage.py populate-db --datadir=../data/test_data --ingest

echo "Installing frontend dependencies"
sudo npm install gulp -g
npm install
sudo gem install sass

gulp
