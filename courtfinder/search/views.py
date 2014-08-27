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
                              'address':address.address.split('\n')})
        court = { 'name': result.name, 'addresses': addresses }
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
        postcode = request.GET['postcode']
        area_of_law = request.GET['area_of_law']

        if postcode == "":
            return redirect('/search/postcode')

        c = CourtSearch()
        results = c.postcode_search(postcode, area_of_law)

        return render(request, 'search/results.jinja', {
            'postcode': postcode,
            'area_of_law': area_of_law,
            'areas_of_law': AreaOfLaw.objects.all(),
            'search_results': format_results(results)
        })
