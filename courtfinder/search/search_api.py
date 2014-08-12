import json
from urllib2 import urlopen

class SearchAPI(object):
    def request(self, user):
        url = "https://api.github.com/users/%s" % user
        response = urlopen(url)

        raw_data = response.read().decode('utf-8')
        return json.loads(raw_data)
