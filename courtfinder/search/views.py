import json
import decimal
import re

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core.serializers.json import DjangoJSONEncoder
from django.views.defaults import bad_request

from search.models import Court, AreaOfLaw, DataStatus
from search.court_search import CourtSearch, CourtSearchError, CourtSearchClientError, CourtSearchInvalidPostcode
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
    "Forced marriage and FGM": "being made to marry or undergo mutilation against your will.",
    "Housing possession": "Evictions and rental disputes.",
    "High court": "",
    "Immigration": "seeking asylum, right to live in the UK and appealing deportation.",
    "Money claims": "small claims, consumer, negligence and personal injury claims.",
    "Probate": "will settlement and disputes.",
    "Social security": "problems with benefits, entitlement, assessment and decisions."
}

def index(request):
    return render(request, 'search/index.jinja')

def aol(request):
    areas_of_law = AreaOfLaw.objects.all().exclude(name='High court').order_by('name')
    aol = request.GET.get('aol', 'All')
    for area in areas_of_law:
        area.description = areas_of_law_description[area.name]
    return render(request, 'search/aol.jinja', {
        'areas_of_law': areas_of_law, 'aol': aol,
    })

def spoe(request):
    aol = request.GET.get('aol', 'All')

    if aol in Rules.has_spoe:
        spoe = request.GET.get('spoe', None)
        return render(request, 'search/spoe.jinja', {
            'aol': aol, 'spoe': spoe,
        })
    else:
        return redirect(reverse('search:postcode')+'?aol='+aol)


def postcode(request):
    aol = request.GET.get('aol', 'All')
    spoe = request.GET.get('spoe', None)
    postcode = request.GET.get('postcode', None)
    error = request.GET.get('error', None)
    params = {
        'aol': aol, 'postcode': postcode, 'error': error
    }
    if spoe:
        params['spoe'] = spoe
    return render(request, 'search/postcode.jinja', params)

def address(request):
    error = request.GET.get('error', None)
    query = request.GET.get('q', None)
    return render(request, 'search/address.jinja', {'error': error, 'query':query})

def results(request):
    query = request.GET.get('q', None)

    if query is not None:
        query = re.sub(r'\s+',' ',query.strip())
        if query == '':
            return redirect(reverse('search:address')+'?error=noquery')
        else:
            results = CourtSearch(query=query).get_courts()

            if len(results) > 0:
                return render(request, 'search/results.jinja', {
                    'query': query,
                    'search_results': __format_results(results)
                })
            else:
                return redirect(reverse('search:address')+'?error=noresults&q='+query)

    else:
        aol = request.GET.get('aol', 'All')
        spoe = request.GET.get('spoe', None)
        postcode = request.GET.get('postcode', None)
        if postcode:
            postcode = re.sub(r'[^A-Za-z0-9 ]','',postcode)
            try:
                courts = CourtSearch(postcode=postcode, area_of_law=aol, single_point_of_entry=spoe).get_courts()
            except CourtSearchInvalidPostcode as e:
                return redirect(reverse('search:postcode')+'?postcode='+
                                postcode+'&error=badpostcode')
            except CourtSearchClientError as e:
                return bad_request(request)

            rules = Rules.for_view(postcode, aol)

            view_obj = {
                'aol': aol, 'spoe': spoe, 'postcode': postcode, 'search_results': __format_results(courts)
            }

            if rules:
                if rules['action'] == 'redirect':
                   return redirect(reverse(rules['target'])+rules.get('params',''))
                elif rules['action'] == 'render':
                    if 'in_scotland' in rules:
                        view_obj['in_scotland'] = rules['in_scotland']

            return render(request, 'search/results.jinja', view_obj)

        else:
            if postcode is not None:
                return redirect(reverse('search:postcode')+
                                '?error=nopostcode'+
                                '&aol='+aol+
                                ('&spoe='+spoe if spoe is not None else ''))
            else:
                return redirect('search:search')


def results_json(request):
    aol = request.GET.get('aol', 'All')
    spoe = request.GET.get('spoe', 'start')
    postcode = request.GET.get('postcode', None)
    query = request.GET.get('q', None)

    try:
        results = CourtSearch(postcode, aol, spoe, query).get_courts()
        return HttpResponse(json.dumps(__format_results(results), default=str),
                            content_type="application/json")
    except CourtSearchError as e:
        return HttpResponseServerError(
                '{"error":"%s"}' % e,
                content_type="application/json")
    except CourtSearchClientError as e:
        return HttpResponseBadRequest(
                '{"error":"%s"}' % e,
                content_type="application/json")



def data_status(request):
    last_change = DataStatus.objects.all().order_by('-last_ingestion_date')[0]
    last_change_object = {
        'last_ingestion_date': last_change.last_ingestion_date,
        'data_hash': last_change.data_hash }
    return HttpResponse(json.dumps(last_change_object, cls=DjangoJSONEncoder), content_type="application/json")


################################################################################
# Private

def __format_results(results):
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
                'county': address.town.county,
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
        dx_contacts = result.courtcontact_set.filter(contact__name='DX')
        if dx_contacts.count() > 0:
            court['dx_number'] = dx_contacts.first().contact.number

        if hasattr(result, 'distance') and result.distance:
            court['distance'] = round(result.distance, 2)

        courts.append(court)
    return courts
