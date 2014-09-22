import json
import decimal
import re

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from search.models import Court, AreaOfLaw, CourtAreasOfLaw
from search.court_search import CourtSearch
from search.rules import Rules

areas_of_law_description = {
    "Adoption": "Applying to adopt a child.",
    "Bankruptcy": "Declaring bankruptcy or being made bankrupt.",
    "Civil partnership": "Ending a civil partnership.",
    "Children": "Child contact issues and disputes over maintenance payments.",
    "Crime": "Being accused of a crime, being a victim or witness.",
    "Divorce": "Ending a marriage.",
    "Domestic violence": "Violence in the home.",
    "Employment": "Workplace disputes including pay, redundancy and discrimination.",
    "Forced marriage": "Being made to marry against your will.",
    "Housing possession": "Evictions and rental disputes.",
    "High court": "",
    "Immigration": "Seeking asylum, establishing right to live in the UK and appealing deportation.",
    "Money claims": "Small claims, consumer claims, negligence and personal injury claims.",
    "Probate": "Will settlement and disputes.",
    "Social security": "Problems with benefits, entitlement, assessment and decisions."
}

whitespace_regex = re.compile(r'\s+')

def index(request):
    return render(request, 'search/index.jinja')


def search_type(request):
    search_type = request.GET.get('type');

    if search_type == 'postcode':
        return redirect(reverse('postcode-view'))
    elif search_type == 'address':
        return redirect(reverse('address-view'))
    else:
        return redirect(reverse('list-view'))


def search_by_postcode(request):
    postcode_requested = request.GET.get('postcode', None)
    area_of_law_requested = request.GET.get('area_of_law', None)
    areas_of_law = AreaOfLaw.objects.all().exclude(name='High court').order_by('name')

    aol_with_copy = []
    for aol in areas_of_law:
        aol.description = areas_of_law_description[aol.name]

    return render(request, 'search/postcode.jinja', {
     'areas_of_law': areas_of_law,
     'area_of_law': area_of_law_requested,
     'postcode': postcode_requested
    })


def list(request):
    #    return render(request, 'search/list.jinja')
    return redirect('https://courttribunalfinder.service.gov.uk/courts')


def search_by_address(request):
    error = request.GET.get('error', False)
    return render(request, 'search/address.jinja', { 'error': error })


def format_results(results):
    """
    create a list of courts from search results that we can send to templates
    """
    courts=[]
    for result in results:
        addresses = result.courtaddress_set.all()
        address = False
        if addresses != []:
            for a in addresses:
                if a.address_type.name == 'Postal':
                    address = a
                    break
                else:
                    address = addresses[0]

        if address:
            visible_address = {
                'address_lines': [line for line in address.address.split('\n') if line != ''],
                'postcode':address.postcode,
                'town':address.town.name,
                'type':address.address_type,
            }
        else:
            visible_address = {}

        areas_of_law=[]
        areas_of_law = [aol for aol in result.areas_of_law.all()]

        court = { 'name': result.name,
                  'lat': result.lat,
                  'lon': result.lon,
                  'number': result.number,
                  'slug': result.slug,
                  'types': [court_type for court_type in result.courtcourttypes_set.all()],
                  'address': visible_address,
                  'areas_of_law': areas_of_law }

        dx_contact = result.courtcontact_set.filter(contact_type__name='DX')
        if dx_contact.count() > 0:
            court['dx_number'] = dx_contact.first().value

        if hasattr(result, 'distance'):
            court['distance'] = round(result.distance, 2)

        courts.append(court)
    return courts

def results_html(request):
    if 'q' in request.GET:
        query = re.sub(whitespace_regex, '', request.GET['q'])

        if query == "":
            return redirect(reverse('address-view')+'?error=1')

        results = CourtSearch.address_search(query)

        return render(request, 'search/results.jinja', {
            'query': query,
            'search_results': format_results(results)
        })
    elif 'postcode' in request.GET:
        postcode = re.sub(whitespace_regex, '', request.GET.get('postcode', ''))
        area_of_law = re.sub(whitespace_regex, '', request.GET.get('area_of_law','All'))

        # error handling
        if postcode == '':
            return redirect(reverse('postcode-view')+'?postcode=')
        if area_of_law == 'unselected':
            return redirect(reverse('postcode-view')+'?postcode='+postcode+'&area_of_law=')

        directive = Rules.for_postcode(postcode, area_of_law)

        if directive['action'] == 'redirect':
            return redirect(directive['target'])
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
            return redirect('/search/')
    else:
        return redirect('/search/')

def results_json(request):
    if 'postcode' in request.GET and 'area_of_law' in request.GET:
        postcode = re.sub(whitespace_regex, '', request.GET.get('postcode', ''))
        area_of_law = re.sub(whitespace_regex, '', request.GET.get('area_of_law','All'))
        directive = Rules.for_postcode(postcode, area_of_law)
        if directive['action'] == 'redirect':
            return redirect(directive['target'])
        elif directive['action'] == 'render':
            results = directive.get('results',None)
        return HttpResponse(json.dumps(format_results(results), default=str), content_type="application/json")
    else:
        return HttpResponse('{}', content_type="application/json")
