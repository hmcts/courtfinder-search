from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='search-view'),
    url(r'^type', views.search_type, name='type-view'),
    url(r'^postcode$', views.search_by_postcode, name='postcode-view'),
    url(r'^address$', views.search_by_address, name='address-view'),
    url(r'^results$', views.results_html, name='result-view'),
    url(r'^results.json$', views.results_json, name='api-result-view'),
)
