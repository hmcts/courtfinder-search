import datetime
import hashlib
import json
import os
from django.conf import settings
from django.db.utils import DatabaseError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
import requests


def healthcheck(request):
    """
    IRaT healthcheck.json: returns status of dependency services
    """
    response = {
        's3_courts_data': {
            'status': 'DOWN',
        },
    }

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

