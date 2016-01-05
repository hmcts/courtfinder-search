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
