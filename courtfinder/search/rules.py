import re
from search.models import Court


class Rules(object):
    scottish_postcodes = ('AB', 'ZE', 'DD', 'KW', 'PH', 'HS', 'IV', 'PA', 'FK',
                          'G', 'ML', 'EH', 'KA', 'KY', 'DG', 'TD')

    by_proximity = ['civil-partnership', 'crime', 'domestic-violence', 'forced-marriage-and-fgm', 'probate']
    by_local_authority = ['adoption', 'children', 'divorce']
    by_postcode = ['bankruptcy', 'housing-possession', 'money-claims']
    has_spoe = ['children', 'divorce', 'money-claims']

    @staticmethod
    def for_view(postcode, area_of_law):
        """
        Returns rules that tell what to render on the screen,
        irrespective of the search. Eg, warnings on some geographical areas
        """
        if Rules._postcode_in_scotland(postcode):
            return {
                'action': 'render',
                'in_scotland': True
            }

        if Rules._postcode_in_NI(postcode):
            if area_of_law == 'immigration':
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
    def for_search(postcode, area_of_law, spoe):
        """
        Does the search and returns a list of courts
        """
        if Rules._postcode_in_NI(postcode):
            if area_of_law == 'immigration':
                return Court.objects.filter(name__icontains='Glasgow Tribunal Hearing Centre')
            else:
                return []

        if spoe and area_of_law == 'money-claims':
            return Court.objects.filter(name__icontains='CCMCC')

        return None

################################################################################
# Private

    @staticmethod
    def _postcode_in_scotland(postcode):
        p = postcode.upper()
        return True if re.match('^G\d+',p) or p[:2] in Rules.scottish_postcodes else False

    @staticmethod
    def _postcode_in_NI(postcode):
        return postcode[:2].lower() == 'bt'
