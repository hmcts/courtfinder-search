import json
import requests
from search.models import Court, AreaOfLaw, CourtAddress

class CourtSearch:

    def postcode_search( self, postcode, area_of_law ):
        try:
            lat, lon = self.postcode_to_latlon( postcode )
        except:
            return []

        area_of_law = AreaOfLaw.objects.get(name=area_of_law)

        results = Court.objects.raw("""
            SELECT *,
                   round((point(c.lon, c.lat) <@> point(%s, %s))::numeric, 3) as distance
              FROM search_court as c,
                   search_courtareasoflaw a
             WHERE c.id = a.court_id
               AND a.area_of_law_id = %s
             ORDER BY (point(c.lon, c.lat) <-> point(%s, %s))
             LIMIT 20
        """, [lon, lat, area_of_law.id, lon, lat])

        return [r for r in results]


    def postcode_to_latlon( self, postcode ):
        """Returns a tuple in the (lat, lon) format"""

        p = postcode.lower().replace(' ', '')
        mapit_url = 'http://mapit.mysociety.org/postcode/%s' % p

        r = requests.get(mapit_url)
        if r.status_code == 200:
            data = json.loads(r.text)

            return (data['wgs84_lat'], data['wgs84_lon'])
        else:
            raise


    def name_search( self, query ):
        results = Court.objects.filter(name__icontains=query)

        return results