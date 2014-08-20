from django.shortcuts import render
from django.http import HttpResponse

from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch

def index(request):
  areas_of_law = AreaOfLaw.objects.all()

  return render(request, 'search/index.jinja', { 
    'areas_of_law': areas_of_law
  })


def postcode_search(request):
  postcode = request.GET['postcode']
  area_of_law = request.GET['area_of_law']

  c = CourtSearch()
  results = c.postcode_search(postcode, AreaOfLaw.objects.get(name='Adoption'))

  return render(request, 'search/postcode.jinja', { 
    'postcode': postcode,
    'area_of_law': area_of_law,
    'search_results': results
  })
