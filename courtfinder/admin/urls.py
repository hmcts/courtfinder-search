from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^courts$', views.courts, name='courts'),
    url(r'^court/(?P<id>[0-9]+)$', views.court, name='court'),
    url(r'^users$', views.users, name='users'),
    url(r'^$', RedirectView.as_view(pattern_name=settings.LOGIN_REDIRECT_URL))
]
