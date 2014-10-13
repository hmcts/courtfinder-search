import json
import decimal
import re

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from search.models import Court, AreaOfLaw
from search.court_search import CourtSearch
from search.rules import Rules

areas_of_law_description = {
    "Adoption": "applying to adopt a child.",
    "Bankruptcy": "declaring bankruptcy or being made bankrupt.",
    "Civil partnership": "ending a civil partnership.",
    "Children": "child contact issues and disputes over maintenance payments.",
    "Crime": "being accused of a crime, being a victim or witness.",
    "Divorce": "ending a marriage.",
    "Domestic violence": "violence in the home.",
    "Employment": "workplace disputes including pay, redundancy and discrimination.",
    "Forced marriage": "being made to marry against your will.",
    "Housing possession": "Evictions and rental disputes.",
    "High court": "",
    "Immigration": "seeking asylum, right to live in the UK and appealing deportation.",
    "Money claims": "small claims, consumer, negligence and personal injury claims.",
    "Probate": "will settlement and disputes.",
    "Social security": "problems with benefits, entitlement, assessment and decisions."
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
        return redirect(reverse('courts:list-view', kwargs={'first_letter':'A'}))


def search_by_postcode(request):
    postcode_requested = request.GET.get('postcode', None)
    area_of_law_requested = request.GET.get('area_of_law', None)
    areas_of_law = AreaOfLaw.objects.all().exclude(name='High court').order_by('name')
    error = request.GET.get('error', False)
    for aol in areas_of_law:
        aol.description = areas_of_law_description[aol.name]

    return render(request, 'search/postcode.jinja', {
      'areas_of_law': areas_of_law,
      'area_of_law': area_of_law_requested,
      'postcode': postcode_requested,
      'error': error,
    })



def search_by_address(request):
    error = request.GET.get('error', False)
    query = request.GET.get('q', None)
    return render(request, 'search/address.jinja', { 'error': error, 'query': query })


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
                'county': address.town.county.name,
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
                  'types': [court_type.court_type.name for court_type in result.courtcourttype_set.all()],
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
        query = re.sub(r'\s+',' ',request.GET.get('q','').strip())

        if query == "":
            return redirect(reverse('address-view')+'?error=noquery')

        results = CourtSearch.address_search(query)
        if len(results) > 0:
            return render(request, 'search/results.jinja', {
                'query': query,
                'search_results': format_results(results)
            })
        else:
            return redirect(reverse('address-view')+'?error=noresults&q='+query)

    elif 'postcode' in request.GET:
        postcode = re.sub(whitespace_regex, '', request.GET.get('postcode', ''))
        area_of_law = request.GET.get('area_of_law','All').strip()

        # error handling
        if postcode == '' or area_of_law == '':
            return redirect(reverse('postcode-view')+'?postcode='+postcode+'&area_of_law='+area_of_law)

        directive = Rules.for_postcode(postcode, area_of_law)

        if directive['action'] == 'redirect':
            return redirect(reverse(directive['target'])+directive.get('params',''))
        elif directive['action'] == 'render':
            results = directive.get('results',None)
            return render(request, 'search/results.jinja', {
                    'postcode': postcode,
                    'area_of_law': area_of_law,
                    'in_scotland': directive.get('in_scotland',False),
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
        area_of_law = request.GET.get('area_of_law','All').strip()
        directive = Rules.for_postcode(postcode, area_of_law)
        if directive['action'] == 'redirect':
            return HttpResponseBadRequest(content_type="application/json")
        elif directive['action'] == 'render':
            results = directive.get('results',None)
        return HttpResponse(json.dumps(format_results(results), default=str), content_type="application/json")
    elif 'q' in request.GET:
        query = request.GET.get('q','').strip()

        if query == "":
            return HttpResponseBadRequest('Empty search query', content_type="application/json")

        results = CourtSearch.address_search(query)
        return HttpResponse(json.dumps(format_results(results), default=str), content_type="application/json")
    else:
        return HttpResponseBadRequest('request needs one of postcode or q parameters', content_type="application/json")
