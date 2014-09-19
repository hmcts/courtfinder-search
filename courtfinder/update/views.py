import json
from django.shortcuts import render
from django.http import *

from search.models import Court

def court(request):
    """
    update a single court from data posted
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], "Only POST allowed")
    court_data_json = request.POST.get('court_data', '')

    try:
        court_data = json.loads(court_data_json)
    except ValueError:
        return HttpResponseBadRequest('Invalid JSON data received: '+court_data_json)

    court_to_change = Court.objects.get(admin_id=court_data['admin_id'])
    court_to_change.name = court_data['name']
    court_to_change.save()

    return HttpResponse('OK')

