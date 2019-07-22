FROM python:3.6

RUN useradd -m -d /srv/search search
WORKDIR /srv/search

# Install system dependencies and generate assets
COPY apt/ ./apt
COPY package.json gulpfile.js ./
COPY docker/ ./docker
COPY courtfinder/assets-src/ ./courtfinder/assets-src
RUN  apt-get clean && apt-get update && ./apt/production.sh \
      && ./docker/setup_npm.sh && npm run gulp && rm -rf ./node_modules \
      && apt-get purge -y --auto-remove ruby npm nodejs \
      && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements/ ./requirements
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static assets
ENV DJANGO_SETTINGS_MODULE courtfinder.settings.production
RUN python courtfinder/manage.py collectstatic --noinput && \
    mkdir -p /srv/logs && chown -R search:search /srv/logs && \
    chown -R search: /srv/search

RUN python courtfinder/manage.py compilemessages

USER search

CMD ./run.sh

EXPOSE 8000
