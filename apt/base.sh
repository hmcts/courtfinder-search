#!/usr/bin/env bash

apt-get install --fix-missing -y --no-install-recommends \
        build-essential \
        git \
        libffi-dev \
        libnet-amazon-s3-tools-perl \
        libpq-dev \
        libssl-dev \
        python-dev \
        python-pip \
        ruby \
        wget
