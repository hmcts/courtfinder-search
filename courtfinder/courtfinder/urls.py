from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^courts/', include('courts.urls', namespace='courts')),
    url(r'', include('healthcheck.urls', namespace='healthcheck')),
    url(r'^', include('staticpages.urls', namespace='staticpages')),
)
