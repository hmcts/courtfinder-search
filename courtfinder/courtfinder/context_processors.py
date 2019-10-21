from django.conf import settings
from django.utils.translation import gettext as _

def globals(request):
    return {
        'app_title': _('Court and tribunal finder'), # Application Title (Populates <title>)
        'proposition_title': _('Court and tribunal finder'), # Proposition Title (Populates proposition header)
        'phase': 'beta', # Current Phase (Sets the current phase and the colour of phase tags). Presumed values: alpha, beta, live
        'product_type': 'service', # Product Type (Adds class to body based on service type). Presumed values: information, service
     }
