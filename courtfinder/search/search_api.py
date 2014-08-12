import json
from urllib2 import urlopen

class SearchAPI(object):
    def request(self, postcode, area_of_law):
        url = "https://courtfinder.is.dsd.io/search?postcode=%s&area_of_law=%s" % (postcode, area_of_law)
        url = url.replace(" ", "+")
        print 'SearchAPI: Calling: %s' % url
        response = urlopen(url)

        raw_data = response.read().decode('utf-8')
        return json.loads(raw_data)
