from search.models import *

class Ingest:
    @classmethod
    def countries(self, countries):
        Country.objects.all().delete()
        County.objects.all().delete()
        Town.objects.all().delete()
        for country in countries:
            c = Country(name=country['name'])
            c.save()
            for county in country['counties']:
                co = County(name=county['name'], country=c)
                co.save()
                for town in county['towns']:
                    if not Town.objects.filter(name=town).exists():
                        t = Town(name=town, county=co)
                        t.save()

    @classmethod
    def courts(self, courts):
        Court.objects.all().delete()
        LocalAuthority.objects.all().delete()
        AreaOfLaw.objects.all().delete()
        CourtAreasOfLaw.objects.all().delete()
        CourtLocalAuthorityAreaOfLaw.objects.all().delete()
        CourtType.objects.all().delete()
        CourtCourtTypes.objects.all().delete()
        CourtAddress.objects.all().delete()
        CourtContact.objects.all().delete()
        ContactType.objects.all().delete()
        CourtPostcodes.objects.all().delete()
        AddressType.objects.all().delete()
        CourtAttributeType.objects.all().delete()
        CourtAttribute.objects.all().delete()
        Facility.objects.all().delete()
        CourtFacilities.objects.all().delete()
        OpeningTime.objects.all().delete()
        CourtOpeningTimes.objects.all().delete()

        for court_obj in courts:
            court = Court(
                admin_id=court_obj['admin_id'],
                name=court_obj['name'],
                slug=court_obj['slug'],
                displayed=court_obj['display'],
                lat=court_obj.get('lat',None),
                lon=court_obj.get('lon',None),
                number=court_obj['court_number'],
                alert=court_obj.get('image_file', None),
                image_file=court_obj.get('image_file', None),
            )
            court.save()

            for aol_obj in court_obj['areas_of_law']:
                aol_name = aol_obj['name']
                aol_councils = aol_obj['councils']

                aol, created = AreaOfLaw.objects.get_or_create(name=aol_name)

                CourtAreasOfLaw.objects.create(court=court, area_of_law=aol)

                for council_name in aol_councils:
                    council, created = LocalAuthority.objects.get_or_create(name=council_name)

                    CourtLocalAuthorityAreaOfLaw.objects.create(
                        court=court,
                        area_of_law=aol,
                        local_authority=council
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
                CourtFacilities.objects.create(court=court, facility=facility)

            for opening_time in court_obj['opening_times']:
                opening_time, created = OpeningTime.objects.get_or_create(description=opening_time)
                CourtOpeningTimes.objects.create(court=court, opening_time=opening_time)

            for court_type_name in court_obj['court_types']:
                ct, created = CourtType.objects.get_or_create(name=court_type_name)

                CourtCourtTypes.objects.create(court=court, court_type=ct)


            for address in court_obj['addresses']:
                address_type, created = AddressType.objects.get_or_create(name=address['type'])
                town, created = Town.objects.get_or_create(name=address['town'])

                CourtAddress.objects.create(
                    court=court,
                    address_type=address_type,
                    address=address['address'],
                    postcode=address['postcode'],
                    town=town
                )

            for contact in court_obj['contacts']:
                contact_type, created = ContactType.objects.get_or_create(name=contact['type'])

                CourtContact.objects.create(
                    court=court,
                    contact_type=contact_type,
                    value=contact['number']
                )

            for postcode in court_obj['postcodes']:
                CourtPostcodes.objects.create(
                    court=court,
                    postcode=postcode
                )
