from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^type', views.search_type, name='type-view'),
    url(r'^postcode$', views.search_by_postcode, name='postcode-view'),
    url(r'^address$', views.search_by_address, name='address-view'),
    url(r'^results$', views.results, name='result-view'),
    url(r'^list$', views.list, name='list-view'),
)
