from django.conf.urls import patterns, url

urlpatterns = patterns('healthcheck.views',
    url(r'^ping.json$', 'ping'),
    url(r'^healthcheck.json$', 'healthcheck'),
    url(r'^pingdom-search-statistics$', 'pingdom_search_statistics'),
)
