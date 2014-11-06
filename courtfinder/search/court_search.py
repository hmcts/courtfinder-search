from collections import OrderedDict
from itertools import chain
import json
import logging
import re

import requests

from django.conf import settings

from search.models import Court, AreaOfLaw, CourtAreaOfLaw, CourtAddress, LocalAuthority, CourtLocalAuthorityAreaOfLaw, CourtPostcode
from search.rules import Rules


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

    def __init__( self, postcode=None, area_of_law=None, single_point_of_entry=False, query=None ):
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
                        loggers['method'].debug('Postcode: %-10s LA: %-20s AOL: %-20s Method: SPOE' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                        return self.__order_by_distance(results)

            results = []

            if isinstance(self.area_of_law, AreaOfLaw):
                if self.area_of_law.name in Rules.by_local_authority:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Local authority search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__local_authority_search()
                elif self.area_of_law.name in Rules.by_postcode:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Postcode search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__postcode_search()

            if len(results) > 0:
                return results

            loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Proximity search' % (self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
            return self.__proximity_search()


    def __local_authority_search( self ):
        if self.postcode.local_authority is None or self.area_of_law is None:
            return []

        covered = CourtLocalAuthorityAreaOfLaw.objects.filter(
            area_of_law=self.area_of_law,
            local_authority__name=self.postcode.local_authority)

        return [c.court for c in covered]


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


    def __dedupe(self, seq):
        """
        remove duplicates from a sequence. Used below for removing dupes in result sets
        From: http://www.peterbe.com/plog/uniqifiers-benchmark
        """
        seen = {}
        result = []
        for item in seq:
            marker = item
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result

    def __postcode_search( self ):
        p = self.postcode.postcode.lower().replace(' ', '')
        results = CourtPostcode.objects.raw("SELECT * FROM search_courtpostcode WHERE (court_id IS NOT NULL and %s like lower(postcode) || '%%') ORDER BY -length(postcode)", [p])
        return self.__dedupe([c.court for c in results])


    def __proximity_search( self ):
        lat = self.postcode.latitude
        lon = self.postcode.longitude

        results = Court.objects.raw("""
            SELECT *,
                   (point(c.lon, c.lat) <@> point(%s, %s)) as distance
              FROM search_court as c
              WHERE c.displayed
             ORDER BY distance
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
        county_results = Court.objects.filter(courtaddress__town__county__name__iregex=query_regex)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(name_results, town_results, address_results, county_results)))

        return [result for result in results if result.displayed]



class Postcode():

    def __init__( self, postcode ):
        self.postcode = postcode

        self.full_postcode = self.is_full_postcode( postcode )
        self.partial_postcode = not self.full_postcode

        self.lookup_postcode()

    def lookup_postcode( self ):
        response = self.mapit( self.postcode )

        if 'wgs84_lat' in response:
            self.latitude = response['wgs84_lat']
            self.longitude = response['wgs84_lon']
        else:
            raise CourtSearchError('MapIt service didn\'t return wgs84 data')

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

        r = self._debug = requests.get(mapit_url)
        if r.status_code == 200:
            try:
                return json.loads(r.text)
            except:
                raise CourtSearchError('MapIt: cannot parse response JSON')
        elif r.status_code in [400, 404]:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchInvalidPostcode('MapIt doesn\'t know this postcode: ' + mapit_url)
        elif r.status_code == 403:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchError('MapIt rate limit exceeded: ' + str(r.status_code))
        else:
            loggers['mapit'].error("%d - %s - %s" % (r.status_code, postcode, r.text))
            raise CourtSearchError('MapIt service error: ' + str(r.status_code))


    def is_full_postcode( self, postcode ):
        # Regex from: https://gist.github.com/simonwhitaker/5748515
        return bool(re.match(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', postcode.upper().replace(' ', '')))

    def __unicode__( self ):
        return self.postcode
