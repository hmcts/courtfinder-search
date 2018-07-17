from django.conf.urls import url
from courts import views

urlpatterns = [
	url(r'^(?P<slug>.+)/leaflet/(?P<leaflet_type>.+)$', views.leaflet, name='leaflet'),
    url(r'^(?P<first_letter>[A-Z])?$', views.list, name='list'),
    url(r'^(?P<slug>.+)\.json$', views.court_json, name='api-court'),
    url(r'^(?P<slug>.+)$', views.court, name='court'),
]

