from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST

# Create your views here.

@require_POST
def update(request):
  if request.POST == {}:
    return HttpResponseBadRequest('{"error": "missing area of law"}')
  return HttpResponse('{"success"}')
