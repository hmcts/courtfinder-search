import re
from search.models import Court
from search.court_search import CourtSearch, CourtSearchInvalidPostcode
from django.core.urlresolvers import reverse

class Rules:

    scottish_postcodes = ('AB', 'ZE', 'DD', 'KW', 'PH', 'HS', 'IV', 'PA', 'FK',
                          'G', 'ML', 'EH', 'KA', 'KY', 'DG', 'TD')


    by_proximity = ['Bankruptcy', 'Civil partnership', 'Crime', 'Domestic violence', 'Forced marriage', 'Probate']
    by_local_authority = ['Adoption', 'Children', 'Divorce', 'Housing possession']
    by_postcode = ['Money claims']
    has_spoe = ['Children', 'Divorce', 'Adoption' ,'Money claims']

    @classmethod
    def __results_or_back(self, postcode, results):
        if len(results) == 0:
            return {
                'action': 'redirect',
                'target': 'search:postcode-view',
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
                    'target': 'search:postcode-view',
                    'params': '?error=ni',
                    }
        else:
            try:
                c = CourtSearch(postcode, area_of_law)
                return Rules.__results_or_back(postcode, c.get_courts())
            except CourtSearchInvalidPostcode:
                return {
                    'action': 'redirect',
                    'target': 'search:postcode-view',
                    'params': '?error=badpc&postcode='+postcode
                }
