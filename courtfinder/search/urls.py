from django.conf.urls import patterns, url
from search import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^postcode$', views.postcode_search),
)
