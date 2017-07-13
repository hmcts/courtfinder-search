FROM python:2.7

RUN useradd -m -d /srv/search search
WORKDIR /srv/search

COPY apt/ ./apt
RUN apt-get update && ./apt/production.sh

COPY package.json gulpfile.js ./
COPY docker/ ./docker
RUN bash ./docker/setup_npm.sh && npm run gulp

COPY requirements/ ./requirements
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production
RUN python courtfinder/manage.py collectstatic --noinput && \
    mkdir -p /srv/logs && chown -R search:search /srv/logs && \
    chown -R search: /srv/search

USER search

CMD ./run.sh

EXPOSE 8000
