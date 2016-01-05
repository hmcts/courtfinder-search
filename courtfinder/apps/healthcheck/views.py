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
from dateutil import tz
from search.models import SearchStatistic


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


def pingdom_search_statistics(request):
    """
    Pingdom custom HTTP check endpoint for IRaT threshold alert
    Check currently determines whether there have been any searches in the past 'grace_time'
    Use 'check_out_of_hours' GET parameter to enable check even out of IRaT hours
    NB: reported response time is meaningless
    """
    def in_hours():
        # 10am to 5pm, Mon to Fri
        now = timezone.now()
        hours = map(lambda hour: datetime.datetime(
            year=now.year, month=now.month, day=now.day,
            hour=hour, tzinfo=tz.gettz('Europe/London'),
        ), [10, 17])
        return now.weekday() not in [5, 6] and hours[0] <= now < hours[1]

    check_out_of_hours = 'check_out_of_hours' in request.GET
    if check_out_of_hours or in_hours():
        try:
            grace_time = int(request.GET['grace_time'])
        except (KeyError, ValueError, TypeError):
            grace_time = 60 * 60  # one hour
        grace_time = datetime.timedelta(seconds=grace_time)
        latest_search = SearchStatistic.get_latest_search()
        no_recent_searches = not latest_search or latest_search < timezone.now() - grace_time
        status = 'NO RECENT SEARCHES' if no_recent_searches else 'OK'
    else:
        status = 'OK'

    return render(request, 'healthcheck/search_statistics.xml', {
        'status': status,
        'response_time': '0',
    }, content_type='application/xml')
