from django.conf.urls import patterns, url
from courts import views

urlpatterns = patterns('',
    url(r'^(?P<first_letter>[A-Z])?$', views.list_view, name='list-view'),
    url(r'^(?P<slug>.+)$', views.court_view, name='court-view'),
)
