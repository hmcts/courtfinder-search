import json
import logging
import re

import requests

from django.conf import settings

from search.models import LocalAuthority
from search.errors import CourtSearchError, CourtSearchInvalidPostcode

loggers = {
    'error': logging.getLogger('search.error'),
    'mapit': logging.getLogger('search.mapit'),
    'la': logging.getLogger('search.la'),
    'aol': logging.getLogger('search.aol'),
    'method': logging.getLogger('search.method'),
}


class PostcodeLookup():

    def __init__(self, postcode):
        self.postcode = Postcode(postcode)
        self.response = None
        self.parsed_response = None

    def url(self):
        """Override in concrete subclasses"""

    def latitude(self):
        """Override in concrete subclasses"""

    def longitude(self):
        """Override in concrete subclasses"""

    def parse(self, text):
        # import pdb; pdb.set_trace()

        self.parsed_response = json.loads(text)

        self.postcode.latitude = self.latitude()
        self.postcode.longitude = self.longitude()

    def headers(self):
        return {}

    def perform(self, headers={}):
        url = self.url()
        r = self._debug = requests.get(url, headers=self.headers())
        self.response = r

        if r.status_code == 200:
            try:
                return self.parse(r.text)
            except CourtSearchInvalidPostcode:
                raise
            except:
                raise CourtSearchError(
                    'cannot parse response JSON from ' + url)
        elif r.status_code in [400, 404]:
            loggers['mapit'].error(
                "%d - %s - %s" %
                (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchInvalidPostcode(
                'Postcode lookup didn\'t know this postcode: ' + url)
        elif r.status_code == 403:
            loggers['mapit'].error(
                "%d - %s - %s" %
                (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchError(
                'Postcode lookup rate limit exceeded: '
                '{url}, {status_code}'.format(
                    url=url, status_code=str(r.status_code)))
        else:
            loggers['mapit'].error(
                "%d - %s - %s" %
                (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchError(
                'Postcode lookup service error: {url}, {status_code}'
                .format(url=url, status_code=str(r.status_code)))

    def supports_local_authority(self):
        """Override in concrete subclasses"""
        return False


class MapitLookup(PostcodeLookup):

    def url(self):
        if self.postcode.full_postcode:
            return settings.MAPIT_BASE_URL + self.postcode.postcode
        else:
            return '{base}partial/{postcode}'.format(
                base=settings.MAPIT_BASE_URL, postcode=self.postcode.postcode)

    def latitude(self):
        if 'wgs84_lat' in self.parsed_response:
            return self.parsed_response['wgs84_lat']
        else:
            raise CourtSearchInvalidPostcode(
                'MapIt service didn\'t return wgs84 data')

    def longitude(self):
        if 'wgs84_lon' in self.parsed_response:
            return self.parsed_response['wgs84_lon']
        else:
            raise CourtSearchInvalidPostcode(
                'MapIt service didn\'t return wgs84 data')

    def supports_local_authority(self):
        return True

    def local_authority_name(self):
        if 'areas' in self.parsed_response:
            return self.parsed_response['areas'][self.__council_id()]['name']

    def local_authority_gss_code(self):
        if 'areas' in self.parsed_response:
            area = self.parsed_response['areas']
            return area[self.__council_id()]['codes']['gss']

    def __council_struct(self):
        return self.parsed_response['shortcuts']['council']

    def __council_id(self):
        council = self.__council_struct()

        if isinstance(council, dict):
            return str(council['county'])
        else:
            return str(council)


class AddressFinderLookup(PostcodeLookup):

    def url(self):
        if self.postcode.full_postcode:
            return settings.ADDRESS_FINDER_BASE_URL + self.postcode.postcode
        else:
            return '{base}partial/{postcode}'.format(
                base=settings.ADDRESS_FINDER_BASE_URL,
                postcode=self.postcode.postcode)

    def headers(self):
        return {'Authorization': 'Token ' + settings.ADDRESS_FINDER_AUTH_TOKEN}

    def latitude(self):
        if 'coordinates' in self.parsed_response:
            return self.parsed_response['coordinates'][1]
        else:
            raise CourtSearchInvalidPostcode(
                'AddressFinder service didn\'t return wgs84 data')

    def longitude(self):
        if 'coordinates' in self.parsed_response:
            return self.parsed_response['coordinates'][0]
        else:
            raise CourtSearchInvalidPostcode(
                'AddressFinder service didn\'t return wgs84 data')


class UkPostcodesLookup(PostcodeLookup):

    def url(self):
        return '{base}{postcode}.json'.format(
            base=settings.UK_POSTCODES_BASE_URL,
            postcode=self.postcode.postcode)

    def latitude(self):
        if 'geo' in self.parsed_response:
            return self.parsed_response['geo']['lat']
        else:
            raise CourtSearchInvalidPostcode(
                'UkPostcodes service didn\'t return wgs84 data')

    def longitude(self):
        if 'geo' in self.parsed_response:
            return self.parsed_response['geo']['lng']
        else:
            raise CourtSearchInvalidPostcode(
                'UkPostcodes service didn\'t return wgs84 data')

    def supports_local_authority(self):
        return True

    def local_authority_name(self):
        if 'administrative' in self.parsed_response:
            return self.parsed_response['administrative']['council']['title']
        else:
            raise CourtSearchInvalidPostcode(
                'UkPostcodes service didn\'t return a local authority name')

    def local_authority_gss_code(self):
        if 'administrative' in self.parsed_response:
            return self.parsed_response['administrative']['council']['code']
        else:
            raise CourtSearchInvalidPostcode(
                'UkPostcodes service didn\'t return'
                ' a local authority gss_code')


class Postcode():

    def __init__(self, postcode):
        self.postcode = postcode
        self.latitude = None
        self.longitude = None
        self.local_authority_name = None
        self.local_authority_gss_code = None
        self.local_authority = None

        self.full_postcode = self.is_full_postcode(postcode)
        self.partial_postcode = not self.full_postcode

    def lookup_postcode(self, service_name='address_finder'):
        lat_long_lookup = self.lookup_service(service_name)
        lat_long_lookup.perform()

        self.latitude = lat_long_lookup.latitude()
        self.longitude = lat_long_lookup.longitude()

    def lookup_local_authority(self,
                               lat_long_lookup=None,
                               council_lookup_service_name='uk_postcodes'):
        if self.local_authority_already_found(lat_long_lookup):
            self.set_local_authority(lat_long_lookup)
        else:
            la_lookup = self.lookup_service(council_lookup_service_name)
            la_lookup.perform()
            self.set_local_authority(la_lookup)

    def set_local_authority(self, lookup):
        self.local_authority_name = lookup.local_authority_name()
        self.local_authority_gss_code = lookup.local_authority_gss_code()

        self.local_authority = self.local_authority_from_db()

    def local_authority_from_db(self):
        try:
            return LocalAuthority.objects.get(
                gss_code=self.local_authority_gss_code)
        except LocalAuthority.DoesNotExist:
            loggers['la'].error(self.local_authority_gss_code)

    def local_authority_already_found(self, lookup_object):
        (
            lookup_object != None
            and lookup_object.supports_local_authority()
            and lookup_object.parsed_response != None
        )

    def lookup_service(self, name='mapit'):
        if name == 'mapit':
            return MapitLookup(self.postcode)
        elif name == 'address_finder':
            return AddressFinderLookup(self.postcode)
        elif name == 'uk_postcodes':
            return UkPostcodesLookup(self.postcode)
        else:
            raise (
                'Unknown Postcode Lookup service requested: ' + name)

    def is_full_postcode(self, postcode):
        # Regex from: https://gist.github.com/simonwhitaker/5748515
        postcode_regex = r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}'
        return bool(re.match(postcode_regex,
                             postcode.upper().replace(' ', '')))

    def __unicode__(self):
        return self.postcode
