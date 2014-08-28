from django.shortcuts import render, redirect
from django.http import HttpResponse
from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch

def index(request):
    return render(request, 'search/index.jinja')


def search_type(request):
    search_type = request.GET.get('type');

    if search_type == 'postcode':
        return redirect('/search/postcode')
    elif search_type == 'address':
        return redirect('/search/address')
    else:
        return redirect('/search/list')


def search_by_postcode(request):
    error = request.GET.get('error', False)

    areas_of_law = AreaOfLaw.objects.all()
    return render(request, 'search/postcode.jinja', {
      'areas_of_law': areas_of_law,
      'error': error
    })


def list(request):
    return render(request, 'search/list.jinja')


def search_by_address(request):
    return render(request, 'search/address.jinja')


def format_results(results):
    """
    create a list of courts from search results that we can send to templates
    """
    courts=[]
    for result in results:
        addresses=[]
        for address in result.courtaddress_set.all():
            addresses.append({'type':address.address_type,
                              'address':address.address.split('\n'),
                              'postcode':address.postcode,
                              'town':address.town.name})
        areas_of_law=[]
        areas_of_law = [aol for aol in result.areas_of_law.all()]

        court = { 'name': result.name,
                  'lat': result.lat,
                  'lon': result.lon,
                  'slug': result.slug,
                  'types': [court_type for court_type in result.courtcourttypes_set.all()],
                  'addresses': addresses,
                  'areas_of_law': areas_of_law }

        dx_contact = result.courtcontact_set.filter(contact_type__name='DX')
        if dx_contact.count() > 0:
            court['dx_number'] = dx_contact.first().value

        if hasattr(result, 'distance'):
            court['distance'] = result.distance

        courts.append(court)
    return courts

def results(request):
    if 'q' in request.GET:
        query = request.GET['q']

        c = CourtSearch()
        results = c.address_search(query)

        return render(request, 'search/results.jinja', {
            'query': query,
            'search_results': format_results(results)
        })
    else:
        postcode = request.GET.get('postcode','')
        area_of_law = request.GET.get('area_of_law','')

        if postcode == "":
            return redirect('/search/postcode?error=1')

        c = CourtSearch()
        results = c.postcode_search(postcode, area_of_law)

        return render(request, 'search/results.jinja', {
            'postcode': postcode,
            'area_of_law': area_of_law,
            'areas_of_law': AreaOfLaw.objects.all(),
            'search_results': format_results(results)
        })
