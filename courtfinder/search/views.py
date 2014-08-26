from django.shortcuts import render, redirect
from django.http import HttpResponse
from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch

def index(request):
  return render(request, 'search/index.jinja')


def search_type(request):
  search_type = request.GET['type'];

  if search_type == 'postcode':
    return redirect('/search/postcode')
  elif search_type == 'address':
    return redirect('/search/address')
  else:
    return redirect('/search/list')


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
  results = c.postcode_search(postcode, area_of_law)

  courts=[]
  for result in results:
    addresses=[]
    for address in result.courtaddress_set.all():
      addresses.append({'type':address.address_type, 'address':address.address.split('\n')})
    court = { 'name': result.name, 'addresses': addresses }
    courts.append(court)


  return render(request, 'search/results.jinja', {
    'postcode': postcode,
    'area_of_law': area_of_law,
    'areas_of_law': AreaOfLaw.objects.all(),
    'search_results': courts
  })
