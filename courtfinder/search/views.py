from django.shortcuts import render
from django.http import HttpResponse

from search.models import Court, AreaOfLaw, CourtAreasOfLaw

def index(request):
  areas_of_law = AreaOfLaw.objects.all()

  return render(request, 'search/index.jinja', { 
    'areas_of_law': areas_of_law 
  })
