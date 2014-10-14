from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', include('staticpages.urls', namespace='staticpages')),
    url(r'^errors/', include('staticpages.urls', namespace='staticpages')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^courts/', include('courts.urls', namespace='courts')),
)
