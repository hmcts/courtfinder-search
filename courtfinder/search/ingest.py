from search.models import *
from dateutil import parser
from django.utils.text import slugify


class Ingest(object):
    @classmethod
    def courts(cls, courts):
        Court.objects.all().delete()
        CourtAttributeType.objects.all().delete()
        CourtAttribute.objects.all().delete()
        CourtPostcode.objects.all().delete()
        AreaOfLaw.objects.all().delete()
        Facility.objects.all().delete()
        OpeningTime.objects.all().delete()
        LocalAuthority.objects.all().delete()
        CourtLocalAuthorityAreaOfLaw.objects.all().delete()
        CourtFacility.objects.all().delete()
        CourtOpeningTime.objects.all().delete()
        CourtAreaOfLaw.objects.all().delete()
        AddressType.objects.all().delete()
        CourtAddress.objects.all().delete()
        Contact.objects.all().delete()
        CourtContact.objects.all().delete()
        Email.objects.all().delete()
        CourtEmail.objects.all().delete()
        CourtType.objects.all().delete()
        CourtCourtType.objects.all().delete()
        DataStatus.objects.all().delete()
        ParkingInfo.objects.all().delete()
        Town.objects.all().delete()

        for court_obj in courts:
            court_created_at = court_obj.get('created_at', None)
            created_at = parser.parse(court_created_at+'UTC') if court_created_at else None
            court_updated_at = court_obj.get('updated_at', None)
            updated_at = parser.parse(court_updated_at+'UTC') if court_updated_at else None
            parking = court_obj.get('parking', None)
            if parking:
                parking_info = ParkingInfo.objects.create(onsite=parking.get('onsite', None),
                                                          offsite=parking.get('offsite', None),
                                                          blue_badge=parking.get('blue_badge', None))
            else:
                parking_info = None

            court = Court(
                admin_id=court_obj['admin_id'],
                cci_code=court_obj.get('cci_code', None),
                name=court_obj['name'],
                slug=court_obj['slug'],
                displayed=court_obj['display'],
                lat=court_obj.get('lat',None),
                lon=court_obj.get('lon',None),
                number=court_obj['court_number'],
                alert=court_obj.get('alert', None),
                directions=court_obj.get('directions', None),
                image_file=court_obj.get('image_file', None),
                created_at=created_at,
                updated_at=updated_at,
                parking=parking_info if parking_info else None,
            )
            court.save()

            for aol_obj in court_obj['areas_of_law']:
                aol_name = aol_obj['name']
                aol_slug = aol_obj.get('slug', slugify(aol_name))
                aol_las = aol_obj['local_authorities']
                aol_spoe = aol_obj.get('single_point_of_entry',False)
                aol, created = AreaOfLaw.objects.get_or_create(name=aol_name, slug=aol_slug)

                CourtAreaOfLaw.objects.create(court=court,
                                              area_of_law=aol,
                                              single_point_of_entry=aol_spoe)

                for local_authority_name in aol_las:
                    local_authority, created = LocalAuthority.objects.get_or_create(name=local_authority_name)

                    CourtLocalAuthorityAreaOfLaw.objects.create(
                        court=court,
                        area_of_law=aol,
                        local_authority=local_authority
                    )

            for facility_obj in court_obj['facilities']:
                facility_name = facility_obj['name']
                facility_description = facility_obj['description']
                facility_image = facility_obj['image']
                facility_image_description = facility_obj['image_description']
                facility, created = Facility.objects.get_or_create(name=facility_name,
                                                                   description=facility_description,
                                                                   image=facility_image,
                                                                   image_description=facility_image_description)
                CourtFacility.objects.create(court=court, facility=facility)

            for opening_time in court_obj['opening_times']:
                opening_time, created = OpeningTime.objects.get_or_create(description=opening_time)
                CourtOpeningTime.objects.create(court=court, opening_time=opening_time)

            for email in court_obj['emails']:
                email, created = Email.objects.get_or_create(description=email['description'], address=email['address'])
                CourtEmail.objects.create(court=court, email=email)

            for court_type_name in court_obj['court_types']:
                ct, created = CourtType.objects.get_or_create(name=court_type_name)

                CourtCourtType.objects.create(court=court, court_type=ct)

            for address in court_obj['addresses']:
                address_type, created = AddressType.objects.get_or_create(name=address['type'])
                town, created = Town.objects.get_or_create(name=address['town'], county=address['county'])

                CourtAddress.objects.create(
                    court=court,
                    address_type=address_type,
                    address=address['address'],
                    postcode=address['postcode'],
                    town=town
                )

            for contact_obj in court_obj['contacts']:
                contact, created = Contact.objects.get_or_create(name=contact_obj['name'],
                                                                 number=contact_obj['number'],
                                                                 sort_order=contact_obj['sort'])

                CourtContact.objects.create(
                    court=court,
                    contact=contact,
                )

            for postcode in court_obj['postcodes']:
                CourtPostcode.objects.create(
                    court=court,
                    postcode=postcode
                )
