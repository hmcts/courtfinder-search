import json
import os
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.utils import DatabaseError
from django.http import JsonResponse
import requests


def ping(request):
    response = {
        'version_number': None,
        'build_date': None,
        'commit_id': None,
        'build_tag': None,
    }
    try:
        with open(os.path.join(settings.PROJECT_ROOT, 'BUILD_VERSION.json')) as f:
            response.update(json.load(f))
    except (IOError, Exception):
        pass
    return JsonResponse(response)


def healthcheck(request):
    response = {
        'database': {
            'status': 'DOWN',
        },
        'mapit': {
            'status': 'DOWN',
        },
        'courtfinder_search': {
            'status': 'DOWN',
        },
        'courtfinder_admin': {
            'status': 'DOWN',
        },
    }

    try:
        from django.db import connections

        conn = connections['default']
        conn.cursor()
        response['database']['status'] = 'UP'
    except (DatabaseError, Exception) as e:
        response['database']['error'] = unicode(e)

    try:
        r = requests.get(settings.MAPIT_BASE_URL + 'SW1A+1AA')
        assert r.status_code == 200, 'MapIt service did not return 200'
        assert r.json(), 'MapIt service did not return valid json'
        response['mapit']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['mapit']['error'] = unicode(e)

    try:
        r = requests.get(request.build_absolute_uri(reverse('search:search')))
        assert r.status_code == 200, 'Start page did not return 200'
        response['courtfinder_search']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['courtfinder_search']['error'] = unicode(e)

    try:
        assert settings.COURTFINDER_ADMIN_HEALTHCHECK, 'Courtfinder Admin healthcheck.json URL not known'
        r = requests.get(settings.COURTFINDER_ADMIN_HEALTHCHECK)
        response['courtfinder_admin']['healthcheck.json'] = r.json()
        assert r.status_code == 200, 'Courtfinder Admin healthcheck.json did not return 200'
        response['courtfinder_admin']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['courtfinder_admin']['error'] = unicode(e)

    fully_working = all(item['status'] == 'UP' for item in response.values())
    return JsonResponse(response, status=200 if fully_working else 503)
