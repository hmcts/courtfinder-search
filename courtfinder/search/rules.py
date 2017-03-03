import re
from search.models import Court
from django.core.urlresolvers import reverse

class Rules:

    scottish_postcodes = ('AB', 'ZE', 'DD', 'KW', 'PH', 'HS', 'IV', 'PA', 'FK',
                          'G', 'ML', 'EH', 'KA', 'KY', 'DG', 'TD')

    by_proximity = ['Crime', 'Domestic violence', 'Forced marriage', 'Probate']
    by_local_authority = ['Adoption', 'Children', 'Divorce', 'Civil partnership']
    by_postcode = ['Bankruptcy', 'Housing possession', 'Money claims']
    has_spoe = ['Children', 'Divorce', 'Money claims', 'Civil partnership']


    @staticmethod
    def for_view(postcode, area_of_law):
        """
        Returns rules that tell what to render on the screen,
        irrespective of the search. Eg, warnings on some geographical areas
        """
        if Rules.__postcode_in_scotland(postcode):
            return {
                'action': 'render',
                'in_scotland': True
            }

        if Rules.__postcode_in_NI(postcode):
            if area_of_law == 'Immigration':
                return {
                    'action': 'render'
                }
            else:
                return {
                    'action': 'redirect',
                    'target': 'search:postcode',
                    'params': '?error=ni'
                }

        return None


    @staticmethod
    def for_search(postcode, area_of_law):
        """
        Does the search and returns a list of courts
        """
        if Rules.__postcode_in_NI(postcode):
            if area_of_law == 'Immigration':
                return Court.objects.filter(name__icontains='Glasgow Tribunal Hearing Centre')
            else:
                return []

        return None

################################################################################
# Private

    @staticmethod
    def __postcode_in_scotland(postcode):
        p = postcode.upper()
        return True if re.match('^G\d+',p) or p[:2] in Rules.scottish_postcodes else False

    @staticmethod
    def __postcode_in_NI(postcode):
        return postcode[:2].lower() == 'bt'
