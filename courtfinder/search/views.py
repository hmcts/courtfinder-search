from django.shortcuts import render, redirect
from django.http import HttpResponse
from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch

def index(request):
  return render(request, 'search/index.jinja')

def search_type(request):
  search_type = request.GET['type'];
  return redirect('/search/'+search_type)

def search_by_postcode(request):
  areas_of_law = AreaOfLaw.objects.all()
  return render(request, 'search/postcode.jinja', {
    'areas_of_law': areas_of_law
  })

def results(request):
  postcode = request.GET['postcode']
  area_of_law = request.GET['area_of_law']

  if postcode == "":
    return redirect('/search/postcode')

  c = CourtSearch()
  results = c.postcode_search(postcode, AreaOfLaw.objects.get(name='Adoption'))
  return render(request, 'search/results.jinja', { 
    'postcode': postcode,
    'area_of_law': area_of_law,
    'search_results': results
  })
