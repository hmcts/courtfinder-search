import json
import requests
from search.models import Court, AreaOfLaw

class CourtSearch:

  def postcode_search( self, postcode, area_of_law ):
    lat, lon = self.postcode_to_latlon( postcode )

    results = Court.objects.raw("""
      SELECT * FROM search_court
        WHERE earth_box(ll_to_earth(%s, %s), 10000) @> ll_to_earth(search_court.lon, search_court.lat)
      """ % (lon, lat))

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
      return None
      
