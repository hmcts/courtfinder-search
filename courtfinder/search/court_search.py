import json
import requests
from itertools import chain
from collections import OrderedDict

from search.models import Court, AreaOfLaw, CourtAddress

class CourtSearch:

    def postcode_search( self, postcode, area_of_law ):
        try:
            lat, lon = self.postcode_to_latlon( postcode )
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


    def postcode_to_latlon( self, postcode ):
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


    def address_search( self, query ):
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
