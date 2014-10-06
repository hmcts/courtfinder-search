import json
import requests
from itertools import chain
from collections import OrderedDict
from django.conf import settings
from search.models import Court, AreaOfLaw, CourtAddress, LocalAuthority, CourtLocalAuthorityAreaOfLaw, CourtPostcodes

class CourtSearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CourtSearchInvalidPostcode(CourtSearchError):
    pass

class CourtSearch:

    @staticmethod
    def local_authority_search( postcode, area_of_law ):
        try:
            la_name = CourtSearch.postcode_to_local_authority(postcode, area_of_law)
        except CourtSearchError:
            return CourtSearch.proximity_search(postcode, area_of_law)
        try:
            la = LocalAuthority.objects.get(name=la_name)
        except LocalAuthority.DoesNotExist:
            return []
        try:
            aol = AreaOfLaw.objects.get(name=area_of_law)
        except AreaOfLaw.DoesNotExist:
            return []

        covered = CourtLocalAuthorityAreaOfLaw.objects.filter(area_of_law=aol, local_authority=la)

        return [c.court for c in covered]

    @staticmethod
    def dedupe(seq):
        """
        remove duplicates from a sequence. Used below for removing dupes in result sets
        From: http://www.peterbe.com/plog/uniqifiers-benchmark
        """
        seen = {}
        result = []
        for item in seq:
            marker = item
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result

    @staticmethod
    def postcode_search(postcode, area_of_law):
        p = postcode.lower().replace(' ', '')
        results = CourtPostcodes.objects.raw("SELECT * FROM search_courtpostcodes WHERE (court_id IS NOT NULL and %s like lower(postcode) || '%%') ORDER BY -length(postcode)", [p])
        return CourtSearch.dedupe([c.court for c in results])


    @staticmethod
    def proximity_search( postcode, area_of_law ):
        lat, lon = CourtSearch.postcode_to_latlon( postcode )
        results = Court.objects.raw("""
            SELECT *,
                   (point(c.lon, c.lat) <@> point(%s, %s)) as distance
              FROM search_court as c
              WHERE c.displayed
             ORDER BY distance
        """, [lon, lat])
        if area_of_law.lower() != 'all':
            try:
                aol = AreaOfLaw.objects.get(name=area_of_law)
            except AreaOfLaw.DoesNotExist:
                return []
            return [r for r in results if aol in r.areas_of_law.all()][:10]
        else:
            return [r for r in results][:10]


    @staticmethod
    def get_from_mapit(mapit_url):
        r = requests.get(mapit_url)
        if r.status_code == 200:
            return r.text
        elif r.status_code in [400, 404]:
            raise CourtSearchInvalidPostcode('Mapit doesn\'t know this postcode: '+mapit_url)
        else:
            raise CourtSearchError('Mapit service error: '+str(r.status_code))

    @staticmethod
    def get_full_postcode(postcode):
        return CourtSearch.get_from_mapit(settings.MAPIT_BASE_URL + postcode)

    @staticmethod
    def get_partial_postcode(postcode):
        return CourtSearch.get_from_mapit(settings.MAPIT_BASE_URL + 'partial/' + postcode)

    @staticmethod
    def postcode_to_latlon(postcode):
        """Returns a tuple in the (lat, lon) format"""
        p = postcode.lower().replace(' ', '')
        if len(postcode) > 4:
            data = CourtSearch.get_full_postcode(p)
        else:
            data = CourtSearch.get_partial_postcode(p)
        if 'wgs84_lat' in data:
            json_data = json.loads(data)
            return (json_data['wgs84_lat'], json_data['wgs84_lon'])
        else:
            raise CourtSearchError('Mapit service didn\'t return wgs84 data')

    @staticmethod
    def postcode_to_local_authority(postcode, area_of_law):
        p = postcode.lower().replace(' ', '')
        if len(postcode) <= 4:
            raise CourtSearchError('Mapit doesn\'t return local authority information for partial postcodes')

        response = CourtSearch.get_full_postcode(p)
        data = json.loads(response)

        if type(data['shortcuts']['council']) == type({}):
            council_id = str(data['shortcuts']['council']['county'])
        else:
            council_id = str(data['shortcuts']['council'])

        return data['areas'][council_id]['name']

    @staticmethod
    def address_search( query ):
        """
        Retrieve name and address search results, order and remove duplicates
        """

        # First we get courts whose name contains the query string
        # (for these courts sorted to show the courts with the highest number of areas of law first)

        name_results =  sorted(Court.objects.filter(name__iregex=r'\y%s\y'%query), key=lambda c: -len(c.areas_of_law.all()))
        # then we get courts with the query string in their address
        address_results = Court.objects.filter(courtaddress__address__iregex=r'\y%s\y'%query)
        # then in the town name
        town_results = Court.objects.filter(courtaddress__town__name__iregex=r'\y%s\y'%query)
        # then the county name
        county_results = Court.objects.filter(courtaddress__town__county__name__iregex=r'\y%s\y'%query)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(name_results, town_results, address_results, county_results)))

        return [result for result in results if result.displayed]
