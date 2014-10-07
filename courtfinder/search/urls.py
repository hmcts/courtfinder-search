from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^type', views.search_type, name='type-view'),
    url(r'^postcode$', views.search_by_postcode, name='postcode-view'),
    url(r'^address$', views.search_by_address, name='address-view'),
    url(r'^results$', views.results_html, name='result-view'),
    url(r'^results.json$', views.results_json, name='api-result-view'),
    url(r'^list$', views.list_view, name='list-view'),
    url(r'^list/(?P<first_letter>[A-Z])$', views.list_view, name='list-view'),
)
