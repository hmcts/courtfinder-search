from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', include('staticpages.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^courts/', include('courts.urls')),
)
