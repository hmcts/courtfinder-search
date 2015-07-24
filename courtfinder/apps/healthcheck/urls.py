# -*- encoding: utf-8 -*-
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'healthcheck.views',

    url(r'^ping.json$', 'ping'),
    url(r'^healthcheck.json$', 'healthcheck'),
)
