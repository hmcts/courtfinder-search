from collections import OrderedDict
from itertools import chain
import json
import logging
import re

import requests

from django.conf import settings

from search.models import Court, AreaOfLaw, CourtAreaOfLaw, CourtAddress, LocalAuthority, CourtLocalAuthorityAreaOfLaw, CourtPostcode
from search.errors import CourtSearchError, CourtSearchClientError, CourtSearchInvalidPostcode

loggers = {
    'error': logging.getLogger('search.error'),
    'mapit': logging.getLogger('search.mapit'),
    'la': logging.getLogger('search.la'),
    'aol': logging.getLogger('search.aol'),
    'method': logging.getLogger('search.method'),
}

class PostcodeLookup():
    def __init__( self, postcode ):
        self.postcode = Postcode(postcode)
        self.response = None
        self.parsed_response = None

    def url( self ):
        """Override in concrete subclasses"""
        
    def latitude( self ):
        """Override in concrete subclasses"""

    def longitude( self ):
        """Override in concrete subclasses"""


    def parse( self, text ):
        # import pdb; pdb.set_trace()

        self.parsed_response = json.loads(text)
        
        self.postcode.latitude = self.latitude()
        self.postcode.longitude = self.longitude()

    def headers( self ):
        return {}

    def perform( self, headers={} ):
        url = self.url()
        r = self._debug = requests.get(url, headers=self.headers())
        self.response = r

        if r.status_code == 200:
            try:
                return self.parse(r.text)
            except CourtSearchInvalidPostcode as e:
                raise
            except:
                raise CourtSearchError('cannot parse response JSON from ' + url)
        elif r.status_code in [400, 404]:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchInvalidPostcode('Postcode lookup didn\'t know this postcode: ' + url)
        elif r.status_code == 403:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchError('Postcode lookup rate limit exceeded: ' + url + ', ' + str(r.status_code))
        else:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, self.postcode.postcode, r.text))
            raise CourtSearchError('Postcode lookup service error: ' + url + ', ' + str(r.status_code))
    


class MapitLookup(PostcodeLookup):
    
    def url( self ):
        if self.postcode.full_postcode:
            return settings.MAPIT_BASE_URL + self.postcode.postcode
        else:
            return settings.MAPIT_BASE_URL + 'partial/' + self.postcode.postcode
        

    def latitude( self ):
        if 'wgs84_lat' in self.parsed_response:
            return self.parsed_response['wgs84_lat']
        else:
            raise CourtSearchInvalidPostcode('MapIt service didn\'t return wgs84 data')

    def longitude( self ):
        if 'wgs84_lon' in self.parsed_response:
            return self.parsed_response['wgs84_lon']
        else:
            raise CourtSearchInvalidPostcode('MapIt service didn\'t return wgs84 data')

    def local_authority( self ):
        if self.postcode.full_postcode:
            local_authority_name = self.local_authority_name()

            try:
                return LocalAuthority.objects.get(name=local_authority_name)
            except LocalAuthority.DoesNotExist:
                loggers['la'].error(local_authority_name)

    def local_authority_name( self ):
        if 'areas' in self.parsed_response:
            return self.parsed_response['areas'][self.__council_id()]['name']

    def __council_struct( self ):
        return self.parsed_response['shortcuts']['council']

    def __council_id( self ):
        council = self.__council_struct()

        if isinstance(council, dict):
            return str(council['county'])
        else:
            return str(council)

    
class AddressFinderLookup(PostcodeLookup):

    def url( self ):
        if self.postcode.full_postcode:
            return settings.ADDRESS_FINDER_BASE_URL + self.postcode.postcode
        else:
            return settings.ADDRESS_FINDER_BASE_URL + 'partial/' + self.postcode.postcode

    def headers( self ):
        return {'Authorization': 'Token ' + settings.ADDRESS_FINDER_AUTH_TOKEN}

    def latitude( self ):
        if 'coordinates' in self.parsed_response:
            return self.parsed_response['coordinates'][1]
        else:
            raise CourtSearchInvalidPostcode('AddressFinder service didn\'t return wgs84 data')

    def longitude( self ):
        if 'coordinates' in self.parsed_response:
            return self.parsed_response['coordinates'][0]
        else:
            raise CourtSearchInvalidPostcode('AddressFinder service didn\'t return wgs84 data')

    def local_authority( self ):
        if self.postcode.full_postcode:
            local_authority_name = self.local_authority_name()

            try:
                return LocalAuthority.objects.get(name=local_authority_name)
            except LocalAuthority.DoesNotExist:
                loggers['la'].error(local_authority_name)

    def local_authority_name( self ):
        return None #self.parsed_response['areas'][self.__council_id()]['name']


class Postcode():

    def __init__( self, postcode ):
        self.postcode = postcode
        self.latitude = None
        self.longitude = None
        self.local_authority_name = None
        self.local_authority = None

        self.full_postcode = self.is_full_postcode( postcode )
        self.partial_postcode = not self.full_postcode

        # self.lookup_postcode()

    def lookup_postcode( self, service_name='mapit' ):
        lookup = self.lookup_service(service_name)
        lookup.perform()
        response = lookup.parsed_response

        self.latitude = lookup.latitude()
        self.longitude = lookup.longitude()

        self.local_authority_name = lookup.local_authority_name()
        self.local_authority = lookup.local_authority()

    def lookup_service(self, name='mapit'):
        if name == 'mapit':
            return MapitLookup( self.postcode )
        elif name == 'address_finder':
            return AddressFinderLookup( self.postcode )
        elif name == 'uk_postcodes_lookup':
            return UkPostcodesLookup( self.postcode )
        else:
            raise UnknownLookupService('Unknown Postcode Lookup service requested: ' + name)


    # def uk_postcodes_lookup( self, postcode ):
    #     if self.full_postcode:
    #         url = settings.UK_POSTCODES_BASE_URL + postcode + '.json'
    #         return self.postcode_lookup(url)
    #     else:
    #         raise CourtSearchInvalidPostcode('Please enter a full postcode: ' + postcode)

    # def address_finder_lookup( self, postcode ):
    #     if self.full_postcode:
    #         url = settings.ADDRESS_FINDER_BASE_URL + postcode
    #         return self.postcode_lookup(url, {'Authorization': 'Token ' + settings.ADDRESS_FINDER_AUTH_TOKEN})
    #     else:
    #         raise CourtSearchInvalidPostcode('Please enter a full postcode: ' + postcode)


    def is_full_postcode( self, postcode ):
        # Regex from: https://gist.github.com/simonwhitaker/5748515
        return bool(re.match(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', postcode.upper().replace(' ', '')))

    def __unicode__( self ):
        return self.postcode

