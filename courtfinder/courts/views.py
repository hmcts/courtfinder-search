import string
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.utils.html import strip_tags
from search.models import Court, AreaOfLaw, Facility
from admin.models import FacilityType

def collapse(source, key, key2):
    """
    Groups objects's key2 by similar key1:

    [{'foo': [1]}, {'bar':[2]}, {'bar':[3]}] => [{'foo': [1], {'bar': [2,3]}}]
    [{'bailiff': [0800383727]}, {'bailiff':[018746]}, {'enquiries':[012874]}] =>
      [{'bailiff': [0800383727, 018746]}, {'enquiries': [012874]}}]
    """
    result = []
    for item in source:
        if len(result) > 0 and item[key] == result[-1][key]:
            result[-1][key2].append(item[key2][0])
        else:
            result.append(item)
    return result


def order_facilities(facility_list):
    ordered_names = FacilityType.objects.all().order_by('order')
    new_list = []
    for o in ordered_names:
        try:
            fac = facility_list.get(name=o.name)
        except Facility.MultipleObjectsReturned:
            fac = facility_list.filter(name=o.name).first()
        except Facility.DoesNotExist:
            fac = None
        if fac:
            new_list.append(fac)
    excluded_facilities = [f for f in facility_list if f not in new_list]
    excluded_facilities = sorted(excluded_facilities, key=lambda x: x.name)
    new_list += excluded_facilities
    return new_list


def format_court(court):
    """
    create a courts object that we can send to templates
    """
    addresses = court.courtaddress_set.all().order_by('address_type__name', '-pk')
    postal_address = None
    visiting_address = None
    for address in addresses:
        address_obj = {
            'address_lines': [line for line in address.address.split('\n') if line != ''],
            'postcode': address.postcode,
            'town': address.town.name,
            'county': address.town.county,
            'type': address.address_type
        }
        if str(address.address_type) == 'Postal' or str(address.address_type) == 'Visit us or write to us':
            postal_address = address_obj
        else:
            visiting_address = address_obj

    if postal_address and str(postal_address['type']) == 'Visit us or write to us':
        visiting_address = None
    court_emails = court.emails.all().order_by('courtemail__order')
    emails = [{'description': email.description, 'addresses': [email.address]} for email in court_emails]
    contacts = [{
        'name': contact.name,
        'numbers': [contact.number],
        'explanation': contact.explanation,
        'in_leaflet': contact.in_leaflet
    } for contact in court.contacts.all().order_by('sort_order')]

    facilities = [
        {
            # Name is used for the css class name to set the x,y offsets on old style images
            'name': facility.name,
            # Description is used for the display text
            'description': facility.description,
            # Image class is the generated class name (empty for new style images)
            'image_class': "" if facility.image_file_path else 'icon-' + facility.image,
            # The relative path to the image
            'image_src': facility.image_file_path if facility.image_file_path else 'images/facility_icons.png',
            # This description is used for the alt text
            'image_description': facility.image_description,
            # The relative file path of the image
            'image_file_path': facility.image_file_path
        }
        for facility in order_facilities(court.facilities.all())
    ]

    court_obj = {
        'name': court.name,
        'displayed': court.displayed,
        'lat': court.lat,
        'lon': court.lon,
        'number': court.number,
        'cci_code': court.cci_code,
        'magistrate_code': court.magistrate_code,
        'updated_at': court.updated_at.strftime("%d %B %Y") if court.updated_at else '',
        'slug': court.slug,
        'image_file': court.image_file,
        'image_url': (settings.COURT_IMAGE_BASE_URL + court.image_file) if court.image_file else '',
        'types': [court_type.court_type.name for court_type in court.courtcourttype_set.all()],
        'postal_address': postal_address,
        'visiting_address': visiting_address,
        'opening_times': court.opening_times.all().order_by("description"),
        'areas_of_law': court.areas_of_law.all().order_by("name"),
        'facilities': facilities,
        'emails': collapse(emails, 'description', 'addresses'),
        'contacts': collapse(contacts, 'name', 'numbers'),
        'directions': court.directions if court.directions else None,
        'alert': court.alert if court.alert and court.alert.strip() != '' else None,
        'parking': court.parking or None,
        'info': court.info,
        'hide_aols': court.hide_aols,
        'info_leaflet': court.info_leaflet,
        'juror_leaflet': court.juror_leaflet,
        'defence_leaflet': court.defence_leaflet,
        'prosecution_leaflet': court.prosecution_leaflet}

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
        'query': request.GET.get('q', ''),
        'aol': request.GET.get('aol', 'All'),
        'spoe': request.GET.get('spoe', None),
        'postcode': request.GET.get('postcode', ''),
        'courtcode': request.GET.get('courtcode', False),
        'feature_leaflet_enabled': settings.FEATURE_LEAFLETS_ENABLED,
    })


def leaflet(request, slug, leaflet_type):
    try:
        court = format_court(Court.objects.get(slug=slug))
    except Court.DoesNotExist:
        raise Http404

    if court['displayed']:
        if leaflet_type == 'venue_information':
            return render(
                request,
                'courts/leaflets/information_leaflet.jinja',
                {
                    'court': court
                }
            )

        if leaflet_type == 'defence_witness_information' and ('Crown Court' in court['types'] or 'Magistrates Court' in court['types']):
            return render(
                request,
                'courts/leaflets/defence_leaflet.jinja',
                {
                    'court': court
                }
            )

        if leaflet_type == 'prosecution_witness_information' and ('Crown Court' in court['types'] or 'Magistrates Court' in court['types']):
            return render(
                request,
                'courts/leaflets/prosecution_leaflet.jinja',
                {
                    'court': court
                }
            )

        if leaflet_type == 'juror_information' and 'Crown Court' in court['types']:
            return render(
                request,
                'courts/leaflets/juror_leaflet.jinja',
                {
                    'court': court,
                    'court_title': 'Local Information for Jurors at the Crown Court at ' + court['name']
                }
            )

    raise Http404('The requested leaflet does not exist.')


def list_format_courts(courts):
    return [{
        'name': court.name,
        'slug': court.slug,
        }
            for court in courts
            if court.displayed
        ]


def list(request, first_letter='A'):
    return render(request, 'courts/list.jinja', {
        'letter': first_letter,
        'letters': string.ascii_uppercase,
        'courts': list_format_courts(Court.objects.filter(name__iregex=r'^'+first_letter).order_by('name')) if first_letter else None
    })
