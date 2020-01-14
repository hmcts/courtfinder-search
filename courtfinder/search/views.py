import json
import re
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.views.defaults import bad_request
from django.utils.translation import gettext as _


from search.models import Court, AreaOfLaw, DataStatus, EmergencyMessage
from search.court_search import CourtSearch, CourtSearchError, CourtSearchClientError, CourtSearchInvalidPostcode
from search.rules import Rules
from core.welsh_utils import display_in_welsh, display_court_in_welsh, translate_attribute, translate_type


areas_of_law_description = {
    _("Adoption"): _("applying to adopt a child."),
    _("Bankruptcy"): _("declaring bankruptcy or being made bankrupt."),
    _("Civil partnership"): _("ending a civil partnership."),
    _("Children"): _("child contact issues and disputes over maintenance payments."),
    _("Crime"): _("being accused of a crime, being a victim or witness."),
    _("Divorce"): _("ending a marriage."),
    _("Domestic violence"): _("violence in the home."),
    _("Employment"): _("workplace disputes including pay, redundancy and discrimination."),
    _("Forced marriage"): _("being made to marry against your will."),
    _("Forced marriage and FGM"): _("being made to marry or undergo mutilation against your will."),
    _("Housing possession"): _("Evictions and rental disputes."),
    _("High court"): _("courts dealing with High Court matters"),
    _("High Court District Registry"): _("courts dealing with High Court matters"),
    _("Immigration"): _("seeking asylum, right to live in the UK and appealing deportation."),
    _("Money claims"): _("small claims, consumer, negligence and personal injury claims."),
    _("Probate"): _("will settlement and disputes."),
    _("Social security"): _("problems with benefits, entitlement, assessment and decisions."),
    _("Tax"): _("appealing a tax decision.")
}


def index(request):
    em = EmergencyMessage.objects.get()
    return render(request, 'search/index.jinja',
        {'emergency_message': em.message_cy if display_in_welsh() else em.message, 'show': em.show})


def searchby(request):
    url = 'search:'
    searchby = request.GET.get('searchby')

    if searchby == 'list':
        url = 'courts:'
        if display_in_welsh():
            searchby = 'welsh_list'

    url = url + searchby
    return HttpResponseRedirect(reverse(url))


def searchbyPostcodeOrCourtList(request):
    url = 'search:postcode'
    aol = request.GET.get('aol')

    if (aol == 'Children' or aol == 'Divorce' or aol == 'Civil partnership') and request.GET.get('spoe') == 'continue':
        url = 'courts:list'

    url = "%s?%s" % (reverse(url), urlencode(request.GET))

    return HttpResponseRedirect(url)


def aol(request):
    areas_of_law = AreaOfLaw.objects.all().exclude(name='High court').order_by('name')
    aol = request.GET.get('aol', 'All')
    for area in areas_of_law:
        area.description = areas_of_law_description.get(area.name, '')
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


def courtcode(request):
    error = request.GET.get('error')
    query = request.GET.get('q')
    return render(request, 'search/courtcode.jinja', {'error': error, 'query' : query})


def results(request):
    query = request.GET.get('q', None)
    courtcode = request.GET.get('courtcode', None)

    if courtcode is not None:
        courtcode = re.sub(r'\s+',' ',courtcode.strip())
        if courtcode == '':
            return redirect(reverse('search:courtcode')+'?error=noquery')
        else:
            results = CourtSearch(query=courtcode, courtcode_search=True).get_courts()

            if len(results) > 0:
                open_court_count = sum(1 for result in results if result.displayed)
                return render(request, 'search/results.jinja', {
                    'query': courtcode,
                    'courtcode_search': True,
                    'search_results': __format_results(results),
                    'open_court_count': open_court_count
                })
            else:
                return redirect(reverse('search:courtcode')+'?error=noresults&q='+courtcode)
    elif query is not None:
        query = re.sub(r'\s+',' ',query.strip())
        if query == '':
            return redirect(reverse('search:address')+'?error=noquery')
        else:

            results = CourtSearch(query=query, courtcode_search=False).get_courts()

            if len(results) == 1 and results[0].displayed == False:
                return redirect(reverse('courts:court', kwargs={'slug': results[0].slug}) + '?q=' + query)
            elif len(results) > 0:
                open_court_count = sum(1 for result in results if result.displayed)
                return render(request, 'search/results.jinja', {
                    'query': query,
                    'courtcode_search': False,
                    'search_results': __format_results(results),
                    'open_court_count': open_court_count
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
                return bad_request(request, e)

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
    except (CourtSearchClientError, CourtSearchInvalidPostcode) as e:
        return HttpResponseBadRequest(
                '{"error":"%s"}' % e,
                content_type="application/json")
    except CourtSearchError as e:
        return HttpResponseServerError(
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

        addresses = result.courtaddress_set.all().order_by("-pk")
        address = False
        if addresses != []:
            for a in addresses:
                if a.address_type.name == 'Postal':
                    address = a
                    break
                else:
                    address = addresses[0]

        if address:
            welsh = display_court_in_welsh(address.court)
            visible_address = {
                'address_lines': [line for line in translate_attribute(address, 'address', welsh).split('\n')
                                  if line != ''],
                'postcode': address.postcode,
                'town': translate_attribute(address, 'town_name', welsh),
                'type': address.address_type,
            }
        else:
            visible_address = {}

        areas_of_law = [
        {
            'name': aol.name if not aol.alt_name else translate_type(AreaOfLaw, aol.alt_name, display_in_welsh(), 'alt_name'),
            'external_link': aol.external_link,
            'display_url': aol.display_url_cy if display_in_welsh() else aol.display_url,
            'external_link_desc': translate_type(AreaOfLaw, aol.external_link_desc,
                                                 display_in_welsh(),
                                                 'external_link_desc')
        } for aol in result.areas_of_law.all()]

        court = { 'name': translate_attribute(result, 'name', display_court_in_welsh(result)),
                  'lat': result.lat,
                  'lon': result.lon,
                  'number': result.number,
                  'cci_code': result.cci_code,
                  'magistrate_code': result.magistrate_code,
                  'slug': result.slug,
                  'types': sorted([court_type.court_type.name for court_type in result.courtcourttype_set.all()]),
                  'address': visible_address,
                  'areas_of_law': areas_of_law,
                  'displayed' : result.displayed,
                  'hide_aols': result.hide_aols}
                  
        dx_contacts = result.courtcontact_set.filter(contact__name='DX')
        if dx_contacts.count() > 0:
            court['dx_number'] = dx_contacts.first().contact.number

        if hasattr(result, 'distance') and result.distance:
            court['distance'] = round(result.distance, 2)

        courts.append(court)
    return courts
