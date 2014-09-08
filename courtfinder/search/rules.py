from search.models import Court
from search.court_search import CourtSearch
from django.core.urlresolvers import reverse

class Rules:

    @classmethod
    def for_postcode(self, postcode, area_of_law):
        if postcode == '':
            return {
                'action': 'redirect',
                'target': reverse('postcode-view') + '?postcode='
            }
        elif postcode[:2].lower() == 'bt':
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
            c = CourtSearch()
            return {
                'action': 'render',
                'results': c.postcode_search(postcode, area_of_law)
            }
