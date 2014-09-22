from django.conf.urls import patterns, url
from update import views

urlpatterns = patterns('',
    url(r'^court$', views.court),
)
