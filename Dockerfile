FROM ubuntu:14.04

RUN useradd -m -d /srv/search search
WORKDIR /srv/search
COPY . .

RUN apt-get clean \
    && apt-get update \
    && ./apt/production.sh

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
