from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='search'),
    url(r'^searchby$', views.searchby, name='searchby'),
    url(r'^aol$', views.aol, name='aol'),
    url(r'^spoe$', views.spoe, name='spoe'),
    url(r'^postcode$', views.postcode, name='postcode'),
    url(r'^results$', views.results, name='results'),

    url(r'^address$', views.address, name='address'),
    url(r'^courtcode$', views.courtcode, name='courtcode'),

    url(r'^results.json$', views.results_json, name='api-results'),
    url(r'^datastatus$', views.data_status, name='data-status'),
)
