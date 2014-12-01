import string
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.html import strip_entities, strip_tags
from search.models import Court, AreaOfLaw


def collapse(source, key, key2):
    """
    Groups objects's key2 by similar key1:

    [{'foo': [1]}, {'bar':[2]}, {'bar':[3]}] => [{'foo': [1], {'bar': [2,3]}}]
    [{'bailiff': [0800383727]}, {'bailiff':[018746]}, {'enquiries':[012874]}] =>
      [{'bailiff': [0800383727, 018746]}, {'enquiries': [012874]}}]
    """
    result=[]
    for item in source:
        if len(result) > 0 and item[key] == result[-1][key]:
            result[-1][key2].append(item[key2][0])
        else:
            result.append(item)
    return result


def format_court(court):
    """
    create a courts object that we can send to templates
    """
    addresses = court.courtaddress_set.all()
    postal_address = None
    visiting_address = None
    for address in addresses:
        address_obj = {
            'address_lines': [line for line in address.address.split('\n') if line != ''],
            'postcode':address.postcode,
            'town':address.town.name,
            'county': address.town.county,
            'type': address.address_type
        }
        if str(address.address_type) == 'Postal':
            postal_address = address_obj
        else:
            visiting_address = address_obj

    emails = [{'description':email.description, 'addresses': [email.address]} for email in court.emails.all()]
    emails.sort(key=lambda x: x['description'])
    contacts = [{'name':contact.name, 'numbers': [contact.number]} for contact in court.contacts.all().order_by('sort_order')]
    # contacts.sort(key=lambda x: x['sort_order'])

    facilities = [{'name': facility.name,
                   'description': strip_entities(strip_tags(facility.description)),
                   'image': facility.image,
                   'image_description': facility.image_description} for facility in court.facilities.all()]

    court_obj = { 'name': court.name,
                  'displayed': court.displayed,
                  'lat': court.lat,
                  'lon': court.lon,
                  'number': court.number,
                  'cci_code': court.cci_code,
                  'updated_at': court.updated_at.strftime("%d %B %Y") if court.updated_at else '',
                  'slug': court.slug,
                  'image_file': court.image_file,
                  'types': [court_type.court_type.name for court_type in court.courtcourttype_set.all()],
                  'postal_address': postal_address,
                  'visiting_address': visiting_address,
                  'opening_times': sorted([opening_time for opening_time in court.opening_times.all()], key=lambda x: x.description),
                  'areas_of_law': sorted([aol for aol in court.areas_of_law.all()]),
                  'facilities': sorted(facilities, key=lambda x: x['name']),
                  'emails': collapse(emails, 'description', 'addresses'),
                  'contacts': collapse(contacts, 'name', 'numbers'),
                  'directions': court.directions if court.directions else None,
                  'alert': court.alert if court.alert and court.alert.strip() != '' else None,
                  'parking': court.parking if court.parking else None,
              }
    dx_contact = court.contacts.filter(courtcontact__contact__name='DX')
    if dx_contact.count() > 0:
        court_obj['dx_number'] = dx_contact.first().number

    return court_obj


def court(request, slug):
    try:
        the_court = Court.objects.get(slug=slug)
    except Court.DoesNotExist:
        raise Http404

    return render(request, 'courts/court.jinja', {
        'court': format_court(the_court),
        'query': request.GET.get('q',''),
        'aol': request.GET.get('aol','All'),
        'spoe': request.GET.get('spoe', None),
        'postcode': request.GET.get('postcode',''),
    })

def list_format_courts(courts):
    return [{'name':court.name,
             'slug':court.slug,
             'numbers': ', '.join(filter(None,('#'+str(court.number) if court.number else None, 'CCI: '+str(court.cci_code) if court.cci_code else None)))
            } for court in courts]

def list(request, first_letter='A'):
    return render(request, 'courts/list.jinja', {
        'letter': first_letter,
        'letters': string.ascii_uppercase,
        'courts': list_format_courts(Court.objects.filter(name__iregex=r'^'+first_letter).order_by('name')) if first_letter else None
    })
