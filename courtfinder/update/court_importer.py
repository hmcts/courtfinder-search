from search.models import *
import json

class CourtImporter:

    @classmethod
    def import_courts(self, courts_obj):
        for court_obj in courts_obj:
            print court_obj
            court = Court(
                admin_id=court_obj['id'],
                name=court_obj['name'],
                slug=court_obj['slug'],
                displayed=court_obj['display'],
                lat=court_obj['latitude'],
                lon=court_obj['longitude'],
                number=court_obj['court_number']
            )
            court.save()
            print 3
            if 'areas_of_law' in court_obj:
                for aol_obj in court_obj['areas_of_law']:
                    print aol_obj
                    aol_name = aol_obj['name']
                    aol_councils = aol_obj['councils']
                    print 3.3
                    aol, created = AreaOfLaw.objects.get_or_create(name=aol_name)
                    print 3.4
                    CourtAreasOfLaw.objects.create(court=court, area_of_law=aol)
                    print 3.5
                    for council_name in aol_councils:
                        council, created = LocalAuthority.objects.get_or_create(name=council_name)

                        CourtLocalAuthorityAreaOfLaw.objects.create(
                            court=court,
                            area_of_law=aol,
                            local_authority=council)
            print 4
            if 'court_types' in court_obj:
                for court_type_name in court_obj['court_types']:
                    ct, created = CourtType.objects.get_or_create(name=court_type_name)

                    CourtCourtTypes.objects.create(court=court, court_type=ct)
            print 5
            if 'addresses' in court_obj:
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
            print 6
            if 'contacts' in court_obj:
                for contact in court_obj['contacts']:
                    contact_type, created = ContactType.objects.get_or_create(name=contact['type'])

                    CourtContact.objects.create(
                        court=court,
                        contact_type=contact_type,
                        value=contact['number']
                    )
            print 7
            if 'postcodes' in court_obj:
                for postcode in court_obj['postcodes']:
                    CourtPostcodes.objects.create(
                        court=court,
                        postcode=postcode
                    )
