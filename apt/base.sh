#!/usr/bin/env bash

apt-get install --fix-missing -y --no-install-recommends \
        postgis \
        python-pip \
        python-dev \
        build-essential \
        wget \
        ruby \
        libpq-dev \
        libnet-amazon-s3-tools-perl \
        git \
        libssl-dev \
        libffi-dev
