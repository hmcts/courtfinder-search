import json
import requests
from itertools import chain
from collections import OrderedDict

from search.models import Court, AreaOfLaw, CourtAddress

class CourtSearch:

    @staticmethod
    def search( postcode=None, area_of_law=None, name=None ):
        if (area_of_law is not None and postcode is None) or (postcode is not None and area_of_law is None):
            raise

    # if area_of_law.type_possession? || area_of_law.type_money_claims?
    #   courts = Court.visible.by_postcode_court_mapping(@query)
    # elsif area_of_law.type_bankruptcy?
    #   #For Bankruptcy, we do an additional check that the postcode matched court also has Bankruptcy listed as an area of law
    #   courts = Court.visible.by_postcode_court_mapping(@query, @options[:area_of_law])
    # elsif area_of_law.type_children? || area_of_law.type_adoption? || area_of_law.type_divorce?
    #   courts = Court.by_area_of_law(@options[:area_of_law]).for_council_and_area_of_law(lookup_council_name, area_of_law)
    # end

        if area_of_law is not None:
            if area_of_law in ['Money claims', 'Housing possession', 'Bankruptcy']:
                CourtSearch.postcode_search(postcode, area_of_law)
            elif area_of_law in ['Children', 'Adoption', 'Divorce' ]:
                CourtSearch.local_authority_search(postcode, area_of_law) 


        if name is not None:
            CourtSearch.address_search(name)


    @staticmethod
    def local_authority_search( postcode, area_of_law ):
        pass


    @staticmethod
    def postcode_search( postcode, area_of_law ):
        pass


    @staticmethod
    def proximity_search( postcode, area_of_law ):
        try:
            lat, lon = CourtSearch.postcode_to_latlon( postcode )
        except:
            return []

        results = Court.objects.raw("""
            SELECT *,
                   round((point(c.lon, c.lat) <@> point(%s, %s))::numeric, 3) as distance
              FROM search_court as c
             ORDER BY (point(c.lon, c.lat) <-> point(%s, %s))
        """, [lon, lat, lon, lat])

        if area_of_law.lower() != 'all':
            aol = AreaOfLaw.objects.get(name=area_of_law)
            return [r for r in results if aol in r.areas_of_law.all()][:10]
        else:
            return [r for r in results][:10]


    @staticmethod
    def postcode_to_latlon( postcode ):
        """Returns a tuple in the (lat, lon) format"""

        p = postcode.lower().replace(' ', '')
        if len(postcode) > 4:
            mapit_url = 'http://mapit.mysociety.org/postcode/%s' % p
        else:
            mapit_url = 'http://mapit.mysociety.org/postcode/partial/%s' % p

        r = requests.get(mapit_url)
        if r.status_code == 200:
            data = json.loads(r.text)

            if 'wgs84_lat' in data:
                return (data['wgs84_lat'], data['wgs84_lon'])
            else:
                raise
        else:
            raise

    @staticmethod
    def postcode_to_local_authority( postcode ):
        p = postcode.lower().replace(' ', '')
        if len(postcode) > 4:
            mapit_url = 'http://mapit.mysociety.org/postcode/%s' % p
        else:
            mapit_url = 'http://mapit.mysociety.org/postcode/partial/%s' % p

        r = requests.get(mapit_url)
        if r.status_code == 200:
            data = json.loads(r.text)

            if !('shortcuts' in data) or !('council' in data['shortcuts']):
                raise

            council_id = data['shortcuts']['council']
            return data['areas'][council_id]['name']
        else:
            raise


    @staticmethod
    def address_search( query ):
        """
        Retrieve name and address search results, order and remove duplicates
        """

        # First we get courts whose name contains the query string
        # (for these courts sorted to show the courts with the highest number of areas of law first)
        name_results =  sorted(Court.objects.filter(name__icontains=query), key=lambda c: -len(c.areas_of_law.all()))
        # then we get courts with the query string in their address
        address_results = Court.objects.filter(courtaddress__address__icontains=query)
        # then in the town name
        town_results = Court.objects.filter(courtaddress__town__name__icontains=query)
        # then the county name
        county_results = Court.objects.filter(courtaddress__town__county__name__icontains=query)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(name_results, town_results, address_results, county_results)))

        return results
