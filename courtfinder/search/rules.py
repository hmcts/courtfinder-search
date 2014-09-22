from search.models import Court
from search.court_search import CourtSearch
from django.core.urlresolvers import reverse

class Rules:

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
                    'action': 'render',
                    'error': 'Aside from immigration tribunals, '
                             'this tool does not return results for Northern Ireland.'
                             'Other courts and tribunals in Northern Ireland are handled'
                             'by the Northern Ireland Courts and Tribunals Service.'
                    }
        elif area_of_law in ['Crime', 'Domestic violence', 'Forced marriage', 'Civil partnership', 'Probate']:
            return {
                'action': 'render',
                'results': CourtSearch.proximity_search(postcode, area_of_law)
            }
        elif area_of_law in ['Money claims', 'Housing possession', 'Bankruptcy']:
            results = CourtSearch.postcode_search(postcode, area_of_law)
            if len(results) == 0:
                results = CourtSearch.proximity_search(postcode, area_of_law)

            return {
                'action': 'render',
                'results': results
            }
        elif area_of_law in ['Children', 'Adoption', 'Divorce']:
            results = CourtSearch.local_authority_search(postcode, area_of_law)
            if len(results) == 0:
                results = CourtSearch.proximity_search(postcode, area_of_law)

            return {
                'action': 'render',
                'results': results
            }
        else:
            return {
                'action': 'render',
                'results': CourtSearch.proximity_search(postcode, area_of_law)
            }

