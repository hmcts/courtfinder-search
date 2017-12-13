from django.conf.urls import include, url

urlpatterns = [
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^courts/', include('courts.urls', namespace='courts')),
    url(r'^', include('staticpages.urls', namespace='staticpages')),
    url(r'^', include('healthcheck.urls', namespace='healthcheck')),
    url(r'^staff/', include('admin.urls', namespace='admin')),
]
