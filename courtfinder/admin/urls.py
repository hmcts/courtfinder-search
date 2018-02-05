from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^courts$', views.courts, name='courts'),
    url(r'^court/(?P<id>[0-9]+)$', views.edit_court, name='court'),
    url(r'^court/address/(?P<id>[0-9]+)$', views.edit_address, name='address'),
    url(r'^court/address/(?P<id>[0-9]+)/(?P<address_id>[0-9]+)$', views.edit_address, name='address'),
    url(r'^court/delete_address/(?P<id>[0-9]+)/(?P<address_id>[0-9]+)$', views.delete_address, name='delete_address'),
    url(r'^users$', views.users, name='users'),
    url(r'^$', RedirectView.as_view(pattern_name=settings.LOGIN_REDIRECT_URL))
]
