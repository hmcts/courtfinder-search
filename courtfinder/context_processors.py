# -*- encoding: utf-8 -*-
"Template context processors"


def globals(request):
    "Context variables used by MOJ Template"

    return {
        # Application Title (Populates <title>)
        'app_title': 'Court and tribunal finder',
        # Proposition Title (Populates proposition header)
        'proposition_title': 'Court and tribunal finder',
        # Current Phase (Sets the current phase and the colour of phase tags).
        # Presumed values: alpha, beta, live
        'phase': 'beta',
        # Product Type (Adds class to body based on service type).
        # Presumed values: information, service
        'product_type': 'service',
    }
