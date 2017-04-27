from collections import OrderedDict
from itertools import chain
import json
import logging
import re

import requests

from django.conf import settings

from search.models import Court, AreaOfLaw, CourtAreaOfLaw, CourtAddress, LocalAuthority, CourtLocalAuthorityAreaOfLaw, CourtPostcode
from search.rules import Rules


MAPIT_HEADERS = {'X-Api-Key': settings.MAPTI_API_KEY if settings.MAPTI_API_KEY else ''}

loggers = {
    'error': logging.getLogger('search.error'),
    'mapit': logging.getLogger('search.mapit'),
    'la': logging.getLogger('search.la'),
    'aol': logging.getLogger('search.aol'),
    'method': logging.getLogger('search.method'),
}

class CourtSearchError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class CourtSearchClientError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value


class CourtSearchInvalidPostcode(CourtSearchError):
    pass

class CourtSearch:

    def __init__( self, postcode=None, area_of_law=None, single_point_of_entry=False, query=None, courtcode_search=False ):
        self.courtcode_search = courtcode_search
        if query:
            self.query = query
        elif postcode:
            self.postcode = Postcode(postcode)
            try:
                if area_of_law.lower() != 'all':
                    self.area_of_law = AreaOfLaw.objects.get(name=area_of_law)
                else:
                    self.area_of_law = AreaOfLaw(name=area_of_law)
            except AreaOfLaw.DoesNotExist:
                loggers['aol'].error(area_of_law)
                raise CourtSearchClientError('bad area of law')

            self.single_point_of_entry = single_point_of_entry
        else:
            raise CourtSearchClientError('bad request')


    def get_courts( self ):
        if hasattr(self, 'query'):
            numberRE = re.compile('^[0-9]{3,4}$')
            courtNumber = numberRE.match(self.query)

            if self.courtcode_search:    
                return self.__court_number_search(self.query)
            else:
                return self.__address_search(self.query)

        else:
            rule_results = Rules.for_search(self.postcode.postcode, self.area_of_law.name)

            if rule_results is not None:
                return rule_results

            if self.single_point_of_entry == 'start':
                if self.area_of_law.name == 'Money claims':
                    return Court.objects.filter(name__icontains='CCMCC')
                elif self.area_of_law.name in Rules.has_spoe:
                    results = [c.court for c in CourtLocalAuthorityAreaOfLaw.objects.filter(area_of_law=self.area_of_law, local_authority=self.postcode.local_authority)]
                    results = [c.court for c in CourtAreaOfLaw.objects.filter(area_of_law=self.area_of_law, single_point_of_entry=True) if c.court in results]

                    if len(results) > 0:
                        loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: SPOE' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                        return self.__order_by_distance(results)

            results = []

            if isinstance(self.area_of_law, AreaOfLaw):
                if self.area_of_law.name in Rules.by_local_authority:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Local authority search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__local_authority_search()
                elif self.area_of_law.name in Rules.by_postcode:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Postcode search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__postcode_search(self.area_of_law)

            if len(results) > 0:
                return self.__order_by_distance(results)

            loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Proximity search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
            return self.__proximity_search()


    def __local_authority_search( self ):
        if self.postcode.local_authority is None or self.area_of_law is None:
            return []

        covered = CourtLocalAuthorityAreaOfLaw.objects.filter(
            area_of_law=self.area_of_law,
            local_authority__name=self.postcode.local_authority)

        return self.__order_by_distance([c.court for c in covered])


    def __order_by_distance( self, courts ):
        if len(courts) == 0:
            return courts

        lat = self.postcode.latitude
        lon = self.postcode.longitude

        court_ids = "(%s)" % ", ".join([str(c.id) for c in courts])

        results = Court.objects.raw("""
                SELECT *,
                       (point(c.lon, c.lat) <@> point(%s, %s)) as distance
                  FROM search_court as c
                 WHERE id in %s
                 ORDER BY distance
        """ % (lon, lat, court_ids))

        return [r for r in results]


    def __postcode_search( self, area_of_law ):
        p = self.postcode.postcode.lower().replace(' ', '')
        results = CourtPostcode.objects \
                .filter(court__areas_of_law=area_of_law) \
                .extra(where=["%s LIKE lower(postcode) || '%%'"], params=[p]) \
                .distinct('court')

        return [c.court for c in results]


    def __proximity_search( self ):
        lat = self.postcode.latitude
        lon = self.postcode.longitude

        results = Court.objects.raw("""
            SELECT *,
                   (point(c.lon, c.lat) <@> point(%s, %s)) as distance
              FROM search_court as c
              WHERE c.displayed
             ORDER BY distance, "name"
        """, [lon, lat])

        if self.area_of_law.name != 'All':
            return [r for r in results if self.area_of_law in r.areas_of_law.all()][:10]
        else:
            return [r for r in results][:10]


    def __address_search( self, query ):
        """
        Retrieve name and address search results, order and remove duplicates
        """

        # First we get courts whose name contains the query string
        # (for these courts sorted to show the courts with the highest number of areas of law first)

        word_separator = re.compile(r'[^\w]+', re.UNICODE)
        query_regex = ''.join(map(lambda word: "(?=.*\y"+word+"\y)", re.split(word_separator, query)))

        name_results =  sorted(Court.objects.filter(name__iregex=query_regex), key=lambda c: -len(c.areas_of_law.all()))
        # then we get courts with the query string in their address
        address_results = Court.objects.filter(courtaddress__address__iregex=query_regex)
        # then in the town name
        town_results = Court.objects.filter(courtaddress__town__name__iregex=query_regex)
        # then the county name
        county_results = Court.objects.filter(courtaddress__town__county__iregex=query_regex)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(name_results, town_results, address_results, county_results)))

        return [result for result in results]

    def __court_number_search( self, query ):
        """
        Retrieve court(s) by court code, order and remove duplicates
        """

        # First we get courts whose court code contains the query string
        # (for these courts sorted to show the courts with the highest number of areas of law first)

        word_separator = re.compile(r'[^\w]+', re.UNICODE)
        query_regex = ''.join(map(lambda word: "(?=.*\y"+word+"\y)", re.split(word_separator, query)))

        court_number_results = Court.objects.filter(number__iregex=query_regex, displayed='True').order_by("name")

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(court_number_results)))

        return results

class Postcode():

    def __init__( self, postcode ):
        self.postcode = re.sub(r'[^A-Za-z0-9 ]','', postcode)

        self.full_postcode = self.is_full_postcode( postcode )
        self.partial_postcode = not self.full_postcode
        self.lookup_postcode()

    def lookup_postcode( self ):
        response = self.mapit( self.postcode )

        if 'wgs84_lat' in response:
            self.latitude = response['wgs84_lat']
            self.longitude = response['wgs84_lon']
        else:
            raise CourtSearchInvalidPostcode('MapIt service didn\'t return wgs84 data')

        if self.full_postcode:
            if isinstance(response['shortcuts']['council'], dict):
                council_id = str(response['shortcuts']['council']['county'])
            else:
                council_id = str(response['shortcuts']['council'])

            local_authority_name = response['areas'][council_id]['name']

            try:
                self.local_authority = LocalAuthority.objects.get(name=local_authority_name)
            except LocalAuthority.DoesNotExist:
                loggers['la'].error(local_authority_name)
                self.local_authority = None

        else:
            self.local_authority = None

    def mapit( self, postcode ):
        if self.full_postcode:
            mapit_url = settings.MAPIT_BASE_URL + postcode
        else:
            mapit_url = settings.MAPIT_BASE_URL + 'partial/' + postcode

        r = self._debug = requests.get(mapit_url, headers=MAPIT_HEADERS)

        self.log_usage(r.headers)

        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                raise CourtSearchError('MapIt: cannot parse response JSON')
        elif r.status_code in [400, 404]:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchInvalidPostcode('MapIt doesn\'t know this postcode: ' + mapit_url)
        elif r.status_code in [403, 429]:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchError('MapIt rate limit exceeded: ' + str(r.status_code))
        else:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchError('MapIt service error: ' + str(r.status_code))

    def log_usage(self, headers):
        usage = self.get_usage(headers)
        usage_message = 'usage: {current}/{limit} ({percent}%)'.format(**usage)

        if usage['percent'] > 95:
            loggers['mapit'].error(usage_message)
        elif usage['percent'] > 80:
            loggers['mapit'].warning(usage_message)
        else:
            loggers['mapit'].info(usage_message)

    def get_usage(self, headers):
        limit = headers.get('X-Quota-Limit')
        current = headers.get('X-Quota-Current')
        percent = None

        if limit is not None and current is not None:
            try:
                current = int(current)
                limit = int(limit)
                percent = int((float(current) / limit) * 100)
            except (ValueError, ZeroDivisionError): # Mapit sent us something unexpected
                pass

        return {'current': current, 'limit': limit, 'percent': percent}

        return 'usage: {}/{} ({})'.format(current, limit, percent)

    def is_full_postcode( self, postcode ):
        # Regex from: https://gist.github.com/simonwhitaker/5748515
        return bool(re.match(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', postcode.upper().replace(' ', '')))

    def __unicode__( self ):
        return self.postcode
