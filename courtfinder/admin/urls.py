from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^auth/', include('django.contrib.auth.urls')),
    url(r'^courts$', views.courts, name='courts'),
    url(r'^court/new$', views.new_court, name='new_court'),
    url(r'^court/(?P<id>[0-9]+)$', views.edit_court, name='court'),
    url(r'^court/(?P<id>[0-9]+)/types$', views.edit_types, name='types'),
    url(r'^court/(?P<id>[0-9]+)/location$', views.edit_location, name='location'),
    url(r'^court/(?P<id>[0-9]+)/location/geo$', views.locate_postcode, name='geolocation'),
    url(r'^court/(?P<id>[0-9]+)/address$', views.edit_address, name='address'),
    url(r'^court/(?P<id>[0-9]+)/address/(?P<address_id>[0-9]+)$', views.edit_address, name='address'),
    url(r'^court/(?P<id>[0-9]+)/delete_address/(?P<address_id>[0-9]+)$', views.delete_address, name='delete_address'),
    url(r'^court/(?P<id>[0-9]+)/contact$', views.ContactFormView.as_view(), name='contact'),
    url(r'^court/(?P<id>[0-9]+)/reorder_contacts', views.ContactReorderView.as_view(), name='reorder_contacts'),
    url(r'^court/(?P<id>[0-9]+)/email$', views.EmailFormView.as_view(), name='email'),
    url(r'^court/(?P<id>[0-9]+)/reorder_emails$', views.EmailReorderView.as_view(), name='reorder_emails'),
    url(r'^court/(?P<id>[0-9]+)/opening_times$', views.OpeningFormView.as_view(), name='opening'),
    url(r'^court/(?P<id>[0-9]+)/reorder_opening_times$', views.OpeningReorderView.as_view(), name='reorder_openings'),
    url(r'^court/(?P<id>[0-9]+)/facility$', views.FacilityFormView.as_view(), name='facility'),
    url(r'^court/(?P<id>[0-9]+)/reorder_facilities$', views.FacilityReorderView.as_view(), name='reorder_facilities'),
    url(r'^court/(?P<id>[0-9]+)/areas_of_law$', views.areas_of_law, name='aols'),
    url(r'^court/(?P<id>[0-9]+)/leaflets$', views.edit_leaflets, name='leaflets'),
    url(r'^court/(?P<id>[0-9]+)/photo$', views.photo_upload, name='photo'),
    url(r'^court/(?P<id>[0-9]+)/photo_delete$', views.photo_delete, name='photo_delete'),
    url(r'^users$', views.users, name='users'),
    url(r'^users/new$', views.add_user, name='add_user'),
    url(r'^users/edit/(?P<username>\S+)$', views.edit_user, name='edit_user'),
    url(r'^users/delete/(?P<username>\S+)$', views.delete_user, name='delete_user'),
    url(r'^users/password/(?P<username>\S+)$', views.change_user_password, name='user_password'),
    url(r'^account$', views.account, name='account'),
    url(r'^emergency$', views.emergency_message, name='emergency'),
    url(r'^$', RedirectView.as_view(pattern_name=settings.LOGIN_REDIRECT_URL))
]
