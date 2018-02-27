from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^courts$', views.courts, name='courts'),
    url(r'^court/(?P<id>[0-9]+)$', views.edit_court, name='court'),
    url(r'^court/(?P<id>[0-9]+)/location$', views.edit_location, name='location'),
    url(r'^court/(?P<id>[0-9]+)/location/geo$', views.locate_postcode, name='geolocation'),
    url(r'^court/(?P<id>[0-9]+)/address$', views.edit_address, name='address'),
    url(r'^court/(?P<id>[0-9]+)/address/(?P<address_id>[0-9]+)$', views.edit_address, name='address'),
    url(r'^court/(?P<id>[0-9]+)/delete_address/(?P<address_id>[0-9]+)$', views.delete_address, name='delete_address'),
    url(r'^court/(?P<id>[0-9]+)/contact$', views.edit_contact, name='contact'),
    url(r'^court/(?P<id>[0-9]+)/reorder_contacts', views.reorder_contacts, name='reorder_contacts'),
    url(r'^users$', views.users, name='users'),
    url(r'^users/new$', views.add_user, name='add_user'),
    url(r'^users/edit/(?P<username>\S+)$', views.edit_user, name='edit_user'),
    url(r'^users/delete/(?P<username>\S+)$', views.delete_user, name='delete_user'),
    url(r'^users/password/(?P<username>\S+)$', views.change_user_password, name='user_password'),
    url(r'^account', views.account, name='account'),
    url(r'^emergency', views.emergency_message, name='emergency'),
    url(r'^$', RedirectView.as_view(pattern_name=settings.LOGIN_REDIRECT_URL))
]
