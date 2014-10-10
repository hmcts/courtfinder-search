from django.conf.urls import patterns, url
from courts import views

urlpatterns = patterns('',
#    url(r'^$', views.index), We'll have to redirect courts/ to search/list (or the other way around)
    url(r'^(?P<slug>.*)$', views.court_view, name='court-view'),
)
