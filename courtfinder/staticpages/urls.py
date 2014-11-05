from django.conf.urls import patterns, url
from staticpages import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='home'),
    url(r'^api(.html)?$', views.api, name='api'),
    url(r'^feedback$', views.feedback, name='feedback'),
    url(r'^feedback_submit$', views.feedback_submit, name='feedback_submit'),
    url(r'^feedback_sent$', views.feedback_sent, name='feedback_sent'),
)
