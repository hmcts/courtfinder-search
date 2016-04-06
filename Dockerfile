FROM ubuntu:14.04

RUN apt-get clean \
    && apt-get update \
    && apt-get install --fix-missing -y \
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
        git
RUN pip install uWSGI==2.0.8

COPY /docker/. /
RUN mv /search /etc/sudoers.d/search; chmod 755 /run.sh; mkdir -p /srv/additional_files
COPY ./package.json /srv/additional_files/package.json
RUN bash /setup_npm.sh; 
RUN useradd -m -d /srv/search search

COPY ./requirements/base.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN sudo -u search mkdir -p /srv/search

COPY . /srv/search

# RUN wget https://courttribunalfinder.service.gov.uk/courts.json -O /srv/search/data/courts.json

WORKDIR /srv/search
# RUN cp -R /srv/node_files/node_modules /srv/search/

WORKDIR /srv/search/courtfinder
ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production
ENV RAILS_ENV production

ADD gulpfile.js /srv/additional_files/gulpfile.js
WORKDIR /srv/additional_files
RUN mkdir -p /srv/additional_files/courtfinder/assets-src && cp -R /srv/search/courtfinder/assets-src/* /srv/additional_files/courtfinder/assets-src
RUN gulp
RUN cp -R /srv/additional_files/* /srv/search

WORKDIR /srv/search
RUN python courtfinder/manage.py collectstatic --noinput

RUN mkdir -p /srv/logs; chown -R search:search /srv/logs
RUN chown -R search: /srv/search

COPY ./docker/run.sh /run.sh
RUN chmod +x /run.sh

USER search

CMD ["/bin/bash", "-l", "/run.sh"]
