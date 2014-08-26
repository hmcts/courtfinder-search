import json
import requests
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
             LIMIT 20
        """, [lon, lat, lon, lat])

        if area_of_law.lower() != 'all':
            aol = AreaOfLaw.objects.get(name=area_of_law)
            return [r for r in results if aol in r.areas_of_law.all()]
        else:
            return [r for r in results]


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
        results = Court.objects.filter(name__icontains=query)

        return [r for r in results]