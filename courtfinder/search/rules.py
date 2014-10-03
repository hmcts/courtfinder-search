import re
from search.models import Court
from search.court_search import CourtSearch, CourtSearchInvalidPostcode
from django.core.urlresolvers import reverse

class Rules:

    scottish_postcodes = ('AB', 'ZE', 'DD', 'KW', 'PH', 'HS', 'IV', 'PA', 'FK',
                          'G', 'ML', 'EH', 'KA', 'KY', 'DG', 'TD')

    @classmethod
    def __results_or_back(self, postcode, results):
        if len(results) == 0:
            return {
                'action': 'redirect',
                'target': 'postcode-view',
                'params': '?error=noresults&postcode='+postcode,
            }
        else:
            in_scotland = True if re.match('^G\d+',postcode) or postcode[:2] in Rules.scottish_postcodes else False
            return {
                'action': 'render',
                'in_scotland': in_scotland,
                'results': results
            }

    @classmethod
    def for_postcode(self, postcode, area_of_law):
        if postcode[:2].lower() == 'bt':
            if area_of_law == 'Immigration':
                return {
                    'action': 'render',
                    'results': Court.objects.filter(name__icontains='Glasgow Tribunal Hearing Centre')
                }
            else:
                return {
                    'action': 'redirect',
                    'target': 'postcode-view',
                    'params': '?error=ni',
                    }
        else:
            try:
                if area_of_law in ['Crime', 'Domestic violence', 'Forced marriage', 'Civil partnership', 'Probate']:
                    results = CourtSearch.proximity_search(postcode, area_of_law)
                    return Rules.__results_or_back(postcode, results)
                elif area_of_law in ['Money claims', 'Housing possession', 'Bankruptcy']:
                    results = CourtSearch.postcode_search(postcode, area_of_law)
                    if len(results) == 0:
                        results = CourtSearch.proximity_search(postcode, area_of_law)
                    return Rules.__results_or_back(postcode, results)
                elif area_of_law in ['Children', 'Adoption', 'Divorce']:
                    results = CourtSearch.local_authority_search(postcode, area_of_law)
                    if len(results) == 0:
                        results = CourtSearch.proximity_search(postcode, area_of_law)
                    return Rules.__results_or_back(postcode, results)
                else:
                    results = CourtSearch.proximity_search(postcode, area_of_law)
                return Rules.__results_or_back(postcode, results)
            except CourtSearchInvalidPostcode:
                return {
                    'action': 'redirect',
                    'target': 'postcode-view',
                    'params': '?error=badpc'
                }
