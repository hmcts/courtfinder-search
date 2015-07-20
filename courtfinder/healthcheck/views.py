import json
import os
from django.conf import settings
from django.db.utils import DatabaseError
from django.http import JsonResponse


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
        }
    }

    try:
        from django.db import connections

        conn = connections['default']
        conn.cursor()
        response['database']['status'] = 'UP'
    except (DatabaseError, Exception) as e:
        response['database']['error'] = unicode(e)

    errors = any(item['status'] == 'DOWN' for item in response.values())
    return JsonResponse(response, status=503 if errors else 200)
