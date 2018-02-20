#!/bin/bash
./courtfinder/manage.py flush --noinput \
    && ./courtfinder/manage.py loaddata  features/fixtures.yaml \
    && behave -Dheadless