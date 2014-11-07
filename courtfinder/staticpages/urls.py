from django.views import defaults
from django.conf.urls import patterns, url
from staticpages import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^400$', defaults.bad_request, name='400'),
    url(r'^403$', defaults.permission_denied, name='403'),
    url(r'^404$', defaults.page_not_found, name='404'),
    url(r'^500$', defaults.server_error, name='500'),
    url(r'^api(.html)?$', views.api, name='api'),
    url(r'^feedback$', views.feedback, name='feedback'),
    url(r'^feedback_submit$', views.feedback_submit, name='feedback_submit'),
    url(r'^feedback_sent$', views.feedback_sent, name='feedback_sent'),
)
