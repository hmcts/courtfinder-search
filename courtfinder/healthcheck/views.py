import datetime
import hashlib
import json
import os
from django.conf import settings
from django.db.utils import DatabaseError
from django.http import JsonResponse
from django.utils import timezone
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
        'courtfinder_admin': {
            'status': 'DOWN',
        },
        's3_courts_data': {
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
        r = requests.get(settings.MAPIT_BASE_URL + 'SW1A+1AA', timeout=10)
        assert r.status_code == 200, 'MapIt service did not return 200'
        assert r.json(), 'MapIt service did not return valid json'
        response['mapit']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['mapit']['error'] = unicode(e)

    try:
        assert settings.COURTFINDER_ADMIN_HEALTHCHECK, 'Courtfinder Admin healthcheck.json URL not known'
        r = requests.get(settings.COURTFINDER_ADMIN_HEALTHCHECK, timeout=10)
        response['courtfinder_admin']['healthcheck.json'] = r.json()
        assert r.status_code == 200, 'Courtfinder Admin healthcheck.json did not return 200'
        response['courtfinder_admin']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['courtfinder_admin']['error'] = unicode(e)

    try:
        assert settings.COURTS_DATA_S3_URL, 'S3 url for courts.json data not known'
        r = requests.get(settings.COURTS_DATA_S3_URL, stream=True, timeout=10)
        assert r.status_code == 200, 'S3 url for courts.json data did not return 200'
        digest = hashlib.md5()
        for chunk in r.iter_content(1024):
            digest.update(chunk)
        response['s3_courts_data']['s3_url'] = settings.COURTS_DATA_S3_URL
        response['s3_courts_data']['s3_hash'] = digest.hexdigest()
        from search.models import DataStatus
        last_ingestion = DataStatus.objects.all().order_by('-last_ingestion_date').first()
        response['s3_courts_data']['local_hash'] = last_ingestion.data_hash
        response['s3_courts_data']['local_date'] = last_ingestion.last_ingestion_date
        assert response['s3_courts_data']['s3_hash'] == last_ingestion.data_hash \
            or timezone.now() - last_ingestion.last_ingestion_date <= datetime.timedelta(minutes=10), \
            'Local courts data is different from S3 and older than 10min'
        response['s3_courts_data']['status'] = 'UP'
    except (requests.RequestException, Exception) as e:
        response['s3_courts_data']['error'] = unicode(e)

    fully_working = all(item['status'] == 'UP' for item in response.values())
    return JsonResponse(response, status=200 if fully_working else 503)
