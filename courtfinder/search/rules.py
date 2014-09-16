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
                    'results': Court.objects.filter(name='Glasgow Tribunal Hearing Centre')
                }
            else:
                return {
                    'action': 'render',
                    'error': 'Aside from immigration tribunals, '
                             'this tool does not return results for Northern Ireland.'
                             'Other courts and tribunals in Northern Ireland are handled'
                             'by the Northern Ireland Courts and Tribunals Service.'
                    }
        else:
            return {
                'action': 'render',
                'results': CourtSearch.postcode_search(postcode, area_of_law)
            }
