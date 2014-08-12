import json
from urllib2 import urlopen

class SearchAPI(object):
    def request(self, user):
        url = "https://courtfinder.is.dsd.io/search/%s" % user
        print 'SearchAPI: Calling: %s' % url
        response = urlopen(url)

        raw_data = response.read().decode('utf-8')
        return json.loads(raw_data)
