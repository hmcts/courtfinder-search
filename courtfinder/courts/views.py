import string
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
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
        if len(result) > 0 and item[key] == result[0][key]:
            result[0][key2].append(item[key2][0])
        else:
            result.insert(0,item)
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
            'county': address.town.county.name,
            'type': address.address_type
        }
        if str(address.address_type) == 'Postal':
            postal_address = address_obj
        else:
            visiting_address = address_obj

    emails = [{'description':email.description, 'addresses': [email.address]} for email in court.emails.all()]
    emails.sort(key=lambda x: x['description'])
    contacts = [{'name':contact.name, 'numbers': [contact.number]} for contact in court.contacts.all()]
    contacts.sort(key=lambda x: x['name'])
    court_obj = { 'name': court.name,
              'lat': court.lat,
              'lon': court.lon,
              'number': court.number,
              'slug': court.slug,
              'image_file': court.image_file,
              'types': [court_type.court_type.name for court_type in court.courtcourttype_set.all()],
              'postal_address': postal_address,
              'visiting_address': visiting_address,
              'opening_times': [opening_time for opening_time in court.opening_times.all()],
              'areas_of_law': [aol for aol in court.areas_of_law.all()],
              'facilities': [facility for facility in court.facilities.all()],
              'emails': collapse(emails, 'description', 'addresses'),
              'contacts': collapse(contacts, 'name', 'numbers'),
              'directions': court.directions if court.directions else None,
              'alert': court.alert if court.alert else None,
    }
    dx_contact = court.contacts.filter(courtcontact__contact__name='DX')
    if dx_contact.count() > 0:
        court_obj['dx_number'] = dx_contact.first().number

    return court_obj


def court_view(request, slug):
    return render(request, 'courts/court.jinja', {
        'court': format_court(Court.objects.get(slug=slug)),
        'query': request.GET.get('q',''),
        'area_of_law': request.GET.get('area_of_law','All'),
        'postcode': request.GET.get('postcode',''),
    })

def courts_view(request):
    return redirect(reverse('courts:list-view', kwargs={'first_letter':'A'}))

def list_view(request, first_letter='A'):
    return render(request, 'courts/list.jinja', {
        'letter': first_letter,
        'letters': string.ascii_uppercase,
        'courts': Court.objects.filter(name__iregex=r'^'+first_letter).order_by('name')
    })
