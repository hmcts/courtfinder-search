from django.db import IntegrityError
from django.utils.text import slugify

from search.models import *

from dateutil import parser

class Ingest:

    @classmethod
    def courts(cls, courts, database_name="default"):
        Court.objects.using(database_name).all().delete()
        CourtAttributeType.objects.using(database_name).all().delete()
        CourtAttribute.objects.using(database_name).all().delete()
        CourtPostcode.objects.using(database_name).all().delete()
        AreaOfLaw.objects.using(database_name).all().delete()
        Facility.objects.using(database_name).all().delete()
        OpeningTime.objects.using(database_name).all().delete()
        LocalAuthority.objects.using(database_name).all().delete()
        CourtLocalAuthorityAreaOfLaw.objects.using(database_name).all().delete()
        CourtFacility.objects.using(database_name).all().delete()
        CourtOpeningTime.objects.using(database_name).all().delete()
        CourtAreaOfLaw.objects.using(database_name).all().delete()
        AddressType.objects.using(database_name).all().delete()
        CourtAddress.objects.using(database_name).all().delete()
        Contact.objects.using(database_name).all().delete()
        CourtContact.objects.using(database_name).all().delete()
        Email.objects.using(database_name).all().delete()
        CourtEmail.objects.using(database_name).all().delete()
        CourtType.objects.using(database_name).all().delete()
        CourtCourtType.objects.using(database_name).all().delete()
        DataStatus.objects.using(database_name).all().delete()
        ParkingInfo.objects.using(database_name).all().delete()
        Town.objects.using(database_name).all().delete()

        for court_obj in courts:
            court_created_at = court_obj.get('created_at', None)
            created_at = parser.parse(court_created_at+'UTC') if court_created_at else None
            court_updated_at = court_obj.get('updated_at', None)
            updated_at = parser.parse(court_updated_at+'UTC') if court_updated_at else None
            parking = court_obj.get('parking', None)
            if parking:
                parking_info = ParkingInfo.objects.db_manager(database_name).create(onsite=parking.get('onsite', None),
                                                          offsite=parking.get(
                                                              'offsite', None),
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
                info=court_obj['info'],
            )
            court.save(using=database_name)

            for aol_obj in court_obj['areas_of_law']:
                aol_name = aol_obj['name']
                aol_slug = aol_obj.get('slug', slugify(aol_name))
                aol_las = aol_obj['local_authorities']
                aol_spoe = aol_obj.get('single_point_of_entry',False)
                aol_external_link = aol_obj['external_link']
                aol_external_link_desc = aol_obj['external_link_desc']

                try:
                    aol, created = AreaOfLaw.objects.db_manager(database_name).get_or_create(name=aol_name,
                        external_link=aol_external_link,external_link_desc=aol_external_link_desc)
                    CourtAreaOfLaw.objects.db_manager(database_name).create(court=court,
                                                area_of_law=aol,
                                                single_point_of_entry=aol_spoe)
                except IntegrityError as e:
                    print("ingest: Duplicate entry aol=%s, slug=%s, skipping..."
                                % (aol_name, aol_slug))

                for local_authority in aol_las:
                    if isinstance(local_authority, dict):
                        local_authority_object, created = LocalAuthority.objects.db_manager(database_name).get_or_create(
                            gss_code=local_authority.get('gss_code'),
                            name=local_authority['name'],
                        )
                    else:
                        local_authority_object, created = LocalAuthority.objects.db_manager(database_name).get_or_create(
                            name=local_authority
                        )

                    CourtLocalAuthorityAreaOfLaw.objects.db_manager(database_name).create(
                        court=court,
                        area_of_law=aol,
                        local_authority=local_authority_object
                    )

            for facility_obj in court_obj['facilities']:
                facility_name = facility_obj['name']
                facility_description = facility_obj['description']
                facility_image = facility_obj['image']
                facility_image_description = facility_obj['image_description']
                facility, created = Facility.objects.db_manager(database_name).get_or_create(name=facility_name,
                                                                   description=facility_description,
                                                                   image=facility_image,
                                                                   image_description=facility_image_description)
                CourtFacility.objects.db_manager(database_name).create(court=court, facility=facility)

            for opening_time in court_obj['opening_times']:
                opening_time, created = OpeningTime.objects.db_manager(database_name).get_or_create(
                    description=opening_time)
                CourtOpeningTime.objects.db_manager(database_name).create(
                    court=court, opening_time=opening_time)

            for email in court_obj['emails']:
                email, created = Email.objects.db_manager(database_name).get_or_create(
                    description=email['description'], address=email['address'])
                CourtEmail.objects.db_manager(database_name).create(court=court, email=email)

            for court_type_name in court_obj['court_types']:
                ct, created = CourtType.objects.db_manager(database_name).get_or_create(
                    name=court_type_name)

                CourtCourtType.objects.db_manager(database_name).create(court=court, court_type=ct)


            for address in court_obj['addresses']:
                address_type, created = AddressType.objects.db_manager(database_name).get_or_create(
                    name=address['type'])

                if address['town'] and not(address['town'].isspace()):
                    town, created = Town.objects.db_manager(database_name).get_or_create(
                        name=address['town'], county=address['county'])
                    if not address['postcode']:
                        address['postcode'] = ""
                    CourtAddress.objects.db_manager(database_name).create(
                        court=court,
                        address_type=address_type,
                        address=address['address'],
                        postcode=address['postcode'],
                        town=town
                    )

            for contact_obj in court_obj['contacts']:
                contact, created = Contact.objects.db_manager(database_name).get_or_create(name=contact_obj['name'],
                                                                 number=contact_obj[
                                                                     'number'],
                                                                 sort_order=contact_obj['sort'])

                CourtContact.objects.db_manager(database_name).create(
                    court=court,
                    contact=contact,
                )

            for postcode in court_obj['postcodes']:
                CourtPostcode.objects.db_manager(database_name).create(
                    court=court,
                    postcode=postcode
                )
