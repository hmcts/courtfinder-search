FROM python:3.6

# Adding argument support for ping.json
ARG APP_VERSION=unknown
ARG APP_BUILD_DATE=unknown
ARG APP_GIT_COMMIT=unknown
ARG APP_BUILD_TAG=unknown

# Setting up ping.json variables
ENV APP_VERSION ${APP_VERSION}
ENV APP_BUILD_DATE ${APP_BUILD_DATE}
ENV APP_GIT_COMMIT ${APP_GIT_COMMIT}
ENV APP_BUILD_TAG ${APP_BUILD_TAG}

RUN useradd -m -d /srv/search search
WORKDIR /srv/search

# Install system dependencies and generate assets
COPY apt/ ./apt
COPY package.json gulpfile.js ./
COPY docker/ ./docker
COPY courtfinder/assets-src/ ./courtfinder/assets-src
RUN apt-get update && ./apt/production.sh \
      && ./docker/setup_npm.sh && npm run gulp && rm -rf ./node_modules \
      && apt-get purge -y --auto-remove ruby npm nodejs \
      && rm -rf /var/lib/apt/lists/*

RUN apt-get update -q && \
    apt-get install -qy vim siege curl wrk sudo --no-install-recommends && apt-get clean && \
    rm -rf /var/lib/apt/lists/* && rm -fr *Release* *Sources* *Packages* && \
    truncate -s 0 /var/log/*log

# Install python dependencies
COPY requirements/ ./requirements
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static assets
ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production
RUN python courtfinder/manage.py compilemessages

#USER search

CMD ./run.sh

EXPOSE 8000
