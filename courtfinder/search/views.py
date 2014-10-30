import json
import decimal
import re

from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core.serializers.json import DjangoJSONEncoder

from search.models import Court, AreaOfLaw, DataStatus
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
        return render(request, 'search/postcode.jinja', {
            'aol': aol
        })


def postcode(request):
    aol = request.GET.get('aol', 'All')
    spoe = request.GET.get('spoe', None)
    postcode = request.GET.get('postcode', None)
    error = request.GET.get('error', None)
    return render(request, 'search/postcode.jinja', {
        'aol': aol, 'spoe': spoe, 'postcode': postcode, 'error': error
    })

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
            results = CourtSearch.address_search(query)
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
            if postcode == '':
                return redirect(reverse('search:postcode')+'?error=nopostcode&aol='+aol+'&spoe'+spoe)
            else:
                courts = CourtSearch(postcode=postcode, area_of_law=aol, single_point_of_entry=spoe).get_courts()
                rules = Rules.for_view(postcode, aol)

                view_obj = {
                    'aol': aol, 'spoe': spoe, 'postcode': postcode, 'search_results': courts
                }

                if rules:
                    if rules['action'] == 'redirect':
                       return redirect(reverse(rules['target'])+rules.get('params',''))
                    elif rules['action'] == 'render':
                        if 'in_scotland' in rules:
                            view_obj['in_scotland'] = rules['in_scotland']

                return render(request, 'search/results.jinja', view_obj)


        else:
            return redirect(reverse('search:search'))

def results_json(request):
    if 'postcode' in request.GET and 'area_of_law' in request.GET:
        postcode = re.sub(r'\s+', '', request.GET.get('postcode', ''))
        area_of_law = request.GET.get('area_of_law','All').strip()
        directive = Rules.for_view(postcode, area_of_law)
        if directive['action'] == 'redirect':
            return HttpResponseBadRequest(content_type="application/json")
        elif directive['action'] == 'render':
            try:
              results = directive.get('results', None)
            except Exception:
                HttpResponseServerError('{"error":"service is unable to fulfill your request"}',
                                        content_type="application/json")
        return HttpResponse(json.dumps(__format_results(results),
                                       default=str),
                            content_type="application/json")
    elif 'q' in request.GET:
        query = request.GET.get('q','').strip()
        if query == "":
            return HttpResponseBadRequest('{"error":"Empty search query"}',
                                          content_type="application/json")
        try:
            results = CourtSearch.address_search(query)
        except Exception:
            return HttpResponseServerError('{"error":"service is unable to fulfill your request"}',
                                           content_type="application/json")
        return HttpResponse(json.dumps(__format_results(results), default=str),
                            content_type="application/json")
    else:
        return HttpResponseBadRequest('{"error":"request needs one of postcode or q parameters"}',
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
        dx_contacts = result.courtcontact_set.filter(contact__name='DX')
        if dx_contacts.count() > 0:
            court['dx_number'] = dx_contacts.first().contact.number

        if hasattr(result, 'distance'):
            court['distance'] = round(result.distance, 2)

        courts.append(court)
    return courts


################################################################################
# old stuff

#def search_by_postcode(request):
#    postcode_requested = request.GET.get('postcode', None)
#    area_of_law_requested = request.GET.get('area_of_law', None)
#    areas_of_law = AreaOfLaw.objects.all().exclude(name='High court').order_by('name')
#    error = request.GET.get('error', False)
#    for aol in areas_of_law:
#        aol.description = areas_of_law_description[aol.name]
#
#    return render(request, 'search/postcode.jinja', {
#      'areas_of_law': areas_of_law,
#      'area_of_law': area_of_law_requested,
#      'postcode': postcode_requested,
#      'error': error,
#    })
#




#def results(request):
#    if 'q' in request.GET:
#        query = re.sub(r'\s+',' ',request.GET.get('q','').strip())
#
#        if query == "":
#            return redirect(reverse('search:address')+'?error=noquery')
#
#        results = CourtSearch.address_search(query)
#        if len(results) > 0:
#            return render(request, 'search/results.jinja', {
#                'query': query,
#                'search_results': __format_results(results)
#            })
#        else:
#            return redirect(reverse('search:address')+'?error=noresults&q='+query)
#
#    elif 'postcode' in request.GET:
#        postcode = re.sub(r'\s+', '', request.GET.get('postcode', ''))
#        area_of_law = request.GET.get('area_of_law','All').strip()
#
#        # error handling
#        if postcode == '' or area_of_law == '':
#            return redirect(reverse('search:postcode')+'?postcode='+postcode+'&area_of_law='+area_of_law)
#
#        directive = Rules.for_postcode(postcode, area_of_law)
#
#        if directive['action'] == 'redirect':
#            return redirect(reverse(directive['target'])+directive.get('params',''))
#        elif directive['action'] == 'render':
#            results = directive.get('results',None)
#            return render(request, 'search/results.jinja', {
#                    'postcode': postcode,
#                    'area_of_law': area_of_law,
#                    'in_scotland': directive.get('in_scotland',False),
#                    'areas_of_law': AreaOfLaw.objects.all(),
#                    'error': directive.get('error', None),
#                    'search_results': __format_results(results) if results else None
#                    })
#        else:
#            return redirect('/search/')
#    else:
#        return redirect('/search/')
