from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST

# Create your views here.

@require_POST
def update(request):
  return HttpResponse('<p></p>')
