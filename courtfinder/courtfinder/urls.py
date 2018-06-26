from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^courts/', include('courts.urls', namespace='courts')),
    url(r'^', include('staticpages.urls', namespace='staticpages')),
    url(r'^', include('healthcheck.urls', namespace='healthcheck')),
    url(r'^staff/', include('admin.urls', namespace='admin')),
    url(r'^admin/$', RedirectView.as_view(pattern_name='admin:courts', permanent=True)),
    url(r"^change-language/$", views.set_language, name="set_language"),
]
