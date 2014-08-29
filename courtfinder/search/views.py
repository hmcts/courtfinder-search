from django.shortcuts import render, redirect
from django.http import HttpResponse
from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch
from search.rules import Rules

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
     postcode_requested = request.GET.get('postcode', None)
     areas_of_law = AreaOfLaw.objects.all()
     return render(request, 'search/postcode.jinja', {
      'areas_of_law': areas_of_law,
      'postcode': postcode_requested
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
        addresses = result.courtaddress_set.all()
        for a in addresses:
            if a.address_type == 'Postal':
                address = a
                break
        else:
            address = addresses[0]

        visible_address = {'address_lines':address.address.split('\n'),
                           'postcode':address.postcode,
                           'town':address.town.name}

        areas_of_law=[]
        areas_of_law = [aol for aol in result.areas_of_law.all()]

        court = { 'name': result.name,
                  'lat': result.lat,
                  'lon': result.lon,
                  'slug': result.slug,
                  'types': [court_type for court_type in result.courtcourttypes_set.all()],
                  'address': visible_address,
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
    elif 'postcode' in request.GET:
        postcode = request.GET.get('postcode', '')
        area_of_law = request.GET.get('area_of_law','All')
        directive = Rules.for_postcode(postcode, area_of_law)

        if directive['action'] == 'redirect':
            return redirect(directive.target)
        elif directive['action'] == 'render':
            results = directive.get('results',None)
            return render(request, 'search/results.jinja', {
                    'postcode': postcode,
                    'area_of_law': area_of_law,
                    'areas_of_law': AreaOfLaw.objects.all(),
                    'error': directive.get('error', None),
                    'search_results': format_results(results) if results else None
                    })
        else:
            return redirect('/search')
    else:
        return redirect('/search')
