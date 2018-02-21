import requests
from django.conf import settings
from ukpostcodeutils.validation import is_valid_postcode, is_valid_partial_postcode


MAPIT_HEADERS = {'X-Api-Key': settings.MAPTI_API_KEY}
BASE_URL = 'https://mapit.mysociety.org'


class MapitException(Exception):
    pass


class NotFound(MapitException):
    pass


class InvalidPostcode(MapitException):
    pass


def api_call(query):
    url = BASE_URL + query
    response = requests.get(url, headers=MAPIT_HEADERS)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise NotFound('Not found: %s' % query)
    else:
        raise MapitException('%s %s %s' % (response.status_code, response.reason, url))


class PartialPostcode:
    def __init__(self, data):
        self._data = data
        self.postcode = data['postcode']

    @property
    def coordinates(self):
        return self._data['wgs84_lat'], self._data['wgs84_lon']


class Postcode(PartialPostcode):
    @property
    def local_authority(self):
        council_id = self._data['shortcuts']['council']
        return self._data['areas'][str(council_id)]['name']


def filter_postcode(validator, input):
    filtered = input.upper().replace(' ', '')
    if not validator(filtered):
        raise InvalidPostcode('Invalid postcode: %s' % filtered)
    return filtered


def postcode(query):
    q = filter_postcode(is_valid_postcode, query)
    data = api_call('/postcode/%s' % q)
    return Postcode(data)


def partial_postcode(query):
    q = filter_postcode(is_valid_partial_postcode, query)
    data = api_call('/postcode/partial/%s' % q)
    return PartialPostcode(data)
