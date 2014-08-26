from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^type', views.search_type),
    url(r'^postcode$', views.search_by_postcode),
    url(r'^results$', views.results),
)
