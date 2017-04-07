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
        git \
        build-essential \
        libssl-dev \
        libffi-dev


RUN useradd -m -d /srv/search search
WORKDIR /srv/search
COPY . .
RUN mv ./docker/search /etc/sudoers.d/search

RUN bash ./docker/setup_npm.sh
RUN gulp

RUN pip install pip --upgrade
RUN pip install -r requirements/production.txt

ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production

RUN python courtfinder/manage.py collectstatic --noinput

RUN mkdir -p /srv/logs; chown -R search:search /srv/logs
RUN chown -R search: /srv/search

USER search

CMD ["/bin/bash", "-l", "./run.sh"]
