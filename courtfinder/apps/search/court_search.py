from collections import OrderedDict
from itertools import chain
import logging
import re

import postcodeinfo

from search.models import Court, AreaOfLaw, CourtAreaOfLaw, \
    CourtLocalAuthorityAreaOfLaw, CourtPostcode, LocalAuthority
from search.rules import Rules
from search.errors import *


loggers = {
    'error': logging.getLogger('search.error'),
    'mapit': logging.getLogger('search.mapit'),
    'la': logging.getLogger('search.la'),
    'aol': logging.getLogger('search.aol'),
    'method': logging.getLogger('search.method'),
}


def is_full_postcode(postcode):
    # this is not meant to be a definitive postcode regex, just enough to
    # distinguish a full postcode (eg: SW1H 9AJ) from a partial one (eg: SW1H)
    return bool(re.match(
        r'[A-Z]{1,2}[0-9][0-9A-Z]?[0-9][A-Z]{2}$',
        postcode.upper().replace(' ', '')))


class CourtSearch(object):

    def __init__(self, query):
        self.query = query

    def _encode_query(self):

        def match_whole_word(word):
            return ur'(?=.*\y{word}\y)'.format(word=word)

        word_separator = re.compile(ur'[^\w]+', re.UNICODE)
        words = re.split(word_separator, self.query)
        return ''.join(map(match_whole_word, words))

    def get_courts(self):
        """
        Retrieve name and address search results, order and remove duplicates
        """

        # First we get courts whose name contains the query string (for these
        # courts sorted to show the courts with the highest number of areas of
        # law first)

        query = self._encode_query()

        def num_areas_of_law_covered(court):
            return -len(court.areas_of_law.all())

        name_results = sorted(
            Court.objects.filter(name__iregex=query),
            key=num_areas_of_law_covered)

        # then we get courts with the query string in their address
        address_results = Court.objects.filter(
            courtaddress__address__iregex=query)

        # then in the town name
        town_results = Court.objects.filter(
            courtaddress__town__name__iregex=query)

        # then the county name
        county_results = Court.objects.filter(
            courtaddress__town__county__iregex=query)

        # put it all together and remove duplicates
        results = list(OrderedDict.fromkeys(chain(
            name_results, town_results, address_results, county_results)))

        return [result for result in results if result.displayed]


class PostcodeCourtSearch(CourtSearch):

    def __init__(self, postcode, area_of_law=None, single_point_of_entry=False):
        client = postcodeinfo.Client()

        if is_full_postcode(postcode):
            self.postcode = client.lookup_postcode(postcode)
        else:
            self.postcode = client.lookup_partial_postcode(postcode)

        try:
            if not self.postcode.valid:
                raise CourtSearchInvalidPostcode('{postcode} not found'.format(
                    postcode=postcode))
        except postcodeinfo.ServerException as server_error:
            raise CourtSearchError(server_error)
        except postcodeinfo.ServiceUnavailable as unavailable:
            raise CourtSearchError(unavailable)

        try:
            if area_of_law == 'all':
                self.area_of_law = AreaOfLaw(name='All', slug='all')
            else:
                self.area_of_law = AreaOfLaw.objects.get(slug=area_of_law)

        except AreaOfLaw.DoesNotExist:
            loggers['aol'].error(area_of_law)
            raise CourtSearchClientError('bad area of law')

        self.single_point_of_entry = single_point_of_entry == 'start'

    def get_courts(self):

        rule_results = Rules.for_search(
            self.postcode.normalised, self.area_of_law.slug,
            self.single_point_of_entry)

        if rule_results is not None:
            return rule_results

        try:
            local_authority = LocalAuthority.objects.get(
                gss_code=self.postcode.local_authority['gss_code'])
        except LocalAuthority.DoesNotExist:
            loggers['la'].error(self.postcode.local_authority['gss_code'])
            raise CourtSearchClientError(
                'unknown local authority gss code {gss_code}'.format(
                    **self.postcode.local_authority))

        def log_search_method(method):
            loggers['method'].debug((
                'Postcode: {postcode:<10} LA: {la:<30} '
                'AOL: {area_of_law:<20} Method: {method}').format(
                    postcode=self.postcode.as_given,
                    la=local_authority,
                    area_of_law=self.area_of_law,
                    method=method))

        if self.single_point_of_entry:

            if self.area_of_law.slug in Rules.has_spoe:

                results = CourtLocalAuthorityAreaOfLaw.objects.filter(
                    area_of_law=self.area_of_law,
                    local_authority=local_authority)

                results = [c.court for c in CourtAreaOfLaw.objects.filter(
                    area_of_law=self.area_of_law,
                    single_point_of_entry=True,
                    court__in=[c.court for c in results])]

                if results:
                    log_search_method('SPOE')
                    return self._order_by_distance(results)

        results = []

        if self.area_of_law.slug in Rules.by_local_authority:
            log_search_method('Local authority search')

            if local_authority:
                results = CourtLocalAuthorityAreaOfLaw.objects.filter(
                    area_of_law=self.area_of_law,
                    local_authority=local_authority)
                results = [c.court for c in results]

        elif self.area_of_law.slug in Rules.by_postcode:
            log_search_method('Postcode search')
            results = self._postcode_search(self.area_of_law)

        if results:
            return self._order_by_distance(results)

        log_search_method('Proximity search')
        return self._proximity_search()

    def _order_by_distance(self, courts):
        if courts:
            courts = list(Court.objects.raw((
                'SELECT *, '
                '(point(c.lon, c.lat) <@> point({lon}, {lat})) as distance '
                'FROM search_court as c '
                'WHERE id in ({court_ids}) '
                'ORDER BY distance').format(
                    lon=self.postcode.longitude,
                    lat=self.postcode.latitude,
                    court_ids=','.join(str(c.id) for c in courts))))

        return courts

    def _postcode_search(self, area_of_law):
        p = self.postcode.normalised
        results = CourtPostcode.objects.raw(
            "SELECT * FROM search_courtpostcode WHERE ("
            "court_id IS NOT NULL and "
            "%s like lower(postcode) || '%%'"
            ") ORDER BY -length(postcode)", [p])

        return filter(
            lambda court: area_of_law in court.areas_of_law.all(),
            list(set([c.court for c in results])))

    def _proximity_search(self):
        results = Court.objects.raw(
            (
                'SELECT *, '
                '(point(c.lon, c.lat) <@> point(%s, %s)) as distance '
                'FROM search_court as c '
                'WHERE c.displayed '
                'ORDER BY distance'),
            [self.postcode.longitude, self.postcode.latitude])

        if self.area_of_law.slug == 'all':
            return [r for r in results][:10]

        return [
            r for r in results
            if self.area_of_law in r.areas_of_law.all()][:10]
