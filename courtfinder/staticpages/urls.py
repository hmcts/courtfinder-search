from django.conf.urls import url
from staticpages import views

app_name='staticpages'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^feedback$', views.feedback, name='feedback'),
    url(r'^feedback_submit$', views.feedback_submit, name='feedback_submit'),
    url(r'^feedback_sent$', views.feedback_sent, name='feedback_sent'),
    url(r'^google8011cb4e48a2df61.html', views.google_verification, name='google_verification'),
]
