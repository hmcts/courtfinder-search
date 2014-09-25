from search.models import Court
from search.court_search import CourtSearch
from django.core.urlresolvers import reverse

class Rules:

    @classmethod
    def __results_or_back(self, postcode, results):
        if len(results) == 0:
            return {
                'action': 'redirect',
                'target': 'postcode-view',
                'params': '?error=noresults&postcode='+postcode,
            }
        else:
            return {
                'action': 'render',
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
        elif area_of_law in ['Crime', 'Domestic violence', 'Forced marriage', 'Civil partnership', 'Probate']:
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
