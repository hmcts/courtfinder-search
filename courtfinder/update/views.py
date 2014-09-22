import json
from django.shortcuts import render
from django.http import *

from search.models import Court

def court(request):

    return HttpResponse('OK')

