from collections import OrderedDict
from itertools import chain
import logging
import re

from search.models import \
    Court, AreaOfLaw, CourtAreaOfLaw, CourtLocalAuthorityAreaOfLaw, CourtPostcode
from search.rules import Rules
from search.postcode_lookups import Postcode
from search.errors import CourtSearchClientError


loggers = {
    'error': logging.getLogger('search.error'),
    'mapit': logging.getLogger('search.mapit'),
    'la': logging.getLogger('search.la'),
    'aol': logging.getLogger('search.aol'),
    'method': logging.getLogger('search.method'),
}


class CourtSearch(object):

    def __init__(self, postcode=None, area_of_law=None, single_point_of_entry=False, query=None):
        if query:
            self.query = query
        elif postcode:
            self.postcode = Postcode(postcode)
            self.postcode.lookup_postcode()
            try:
                if area_of_law == 'all':
                    self.area_of_law = AreaOfLaw(name='All', slug='all')
                else:
                    self.area_of_law = AreaOfLaw.objects.get(slug=area_of_law)
            except AreaOfLaw.DoesNotExist:
                loggers['aol'].error(area_of_law)
                raise CourtSearchClientError('bad area of law')

            self.single_point_of_entry = single_point_of_entry
        else:
            raise CourtSearchClientError('bad request')

    def get_courts(self):
        if hasattr(self, 'query'):
            return self.__address_search(self.query)
        else:
            rule_results = Rules.for_search(
                self.postcode.postcode, self.area_of_law.name)

            if rule_results is not None:
                return rule_results

            if self.single_point_of_entry == 'start':
                if self.area_of_law.slug == 'money-claims':
                    return Court.objects.filter(name__icontains='CCMCC')
                elif self.area_of_law.name in Rules.has_spoe:
                    results = [c.court for c in CourtLocalAuthorityAreaOfLaw.objects.filter(
                        area_of_law=self.area_of_law, local_authority=self.postcode.local_authority)]
                    results = [c.court for c in CourtAreaOfLaw.objects.filter(
                        area_of_law=self.area_of_law, single_point_of_entry=True) if c.court in results]

                    if len(results) > 0:
                        loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: SPOE' % (
                            self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                        return self.__order_by_distance(results)

            results = []

            if isinstance(self.area_of_law, AreaOfLaw):
                if self.area_of_law.name in Rules.by_local_authority:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Local authority search' % (
                        self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__local_authority_search()
                elif self.area_of_law.name in Rules.by_postcode:
                    loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Postcode search' % (
                        self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
                    results = self.__postcode_search(self.area_of_law)

            if len(results) > 0:
                return self.__order_by_distance(results)

            loggers['method'].debug('Postcode: %-10s LA: %-30s AOL: %-20s Method: Proximity search' % (
                self.postcode.postcode, self.postcode.local_authority, self.area_of_law))
            return self.__proximity_search()

    def __local_authority_search(self):
        if self.postcode.local_authority is None or self.area_of_law is None:
            return []

        covered = CourtLocalAuthorityAreaOfLaw.objects.filter(
            area_of_law=self.area_of_law,
            local_authority__name=self.postcode.local_authority)

        return self.__order_by_distance([c.court for c in covered])

    def __order_by_distance(self, courts):

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
            if marker in seen:
                continue
            seen[marker] = 1
            result.append(item)
        return result

    def __postcode_search(self, area_of_law):
        p = self.postcode.postcode.lower().replace(' ', '')
        results = CourtPostcode.objects.raw(
            "SELECT * FROM search_courtpostcode WHERE (court_id IS NOT NULL and %s like lower(postcode) || '%%') ORDER BY -length(postcode)", [p])

        return filter(lambda court: area_of_law in court.areas_of_law.all(),
                      self.__dedupe([c.court for c in results]))

    def __proximity_search(self):
        lat = self.postcode.latitude
        lon = self.postcode.longitude

        results = Court.objects.raw("""
            SELECT *,
                   (point(c.lon, c.lat) <@> point(%s, %s)) as distance
              FROM search_court as c
              WHERE c.displayed
             ORDER BY distance
        """, [lon, lat])

        if self.area_of_law.slug != 'all':
            return [r for r in results if self.area_of_law in r.areas_of_law.all()][:10]
        else:
            return [r for r in results][:10]

    def __address_search(self, query):
        """
        Retrieve name and address search results, order and remove duplicates
        """

        # First we get courts whose name contains the query string
        # (for these courts sorted to show the courts with the highest number of areas of law first)

        word_separator = re.compile(r'[^\w]+', re.UNICODE)
        query_regex = ''.join(
            map(lambda word: "(?=.*\y"+word+"\y)", re.split(word_separator, query)))

        name_results = sorted(Court.objects.filter(
            name__iregex=query_regex), key=lambda c: -len(c.areas_of_law.all()))
        # then we get courts with the query string in their address
        address_results = Court.objects.filter(
            courtaddress__address__iregex=query_regex)
        # then in the town name
        town_results = Court.objects.filter(
            courtaddress__town__name__iregex=query_regex)
        # then the county name
        county_results = Court.objects.filter(
            courtaddress__town__county__iregex=query_regex)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(
            chain(name_results, town_results, address_results, county_results)))

        return [result for result in results if result.displayed]
