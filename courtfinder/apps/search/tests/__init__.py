import contextlib
from mock import patch


@contextlib.contextmanager
def postcode_valid(lookup, **kwargs):
    with patch('postcodeinfo.Client') as Client:
        client = Client.return_value
        lookup = getattr(client, lookup)
        postcode = lookup.return_value
        postcode.normalised = kwargs.get('postcode', 'SE15 4UH')
        postcode.local_authority = kwargs.get('local_authority', {
            'name': 'Southwark',
            'gss_code': 'E09000028'})
        postcode.longitude = kwargs.get('lon', -2.359323760375266)
        postcode.latitude = kwargs.get('lat', 53.7491281247251)
        yield


@contextlib.contextmanager
def postcode_error(exception):

    def raise_exception(*args, **kwargs):
        raise exception()

    with patch('postcodeinfo.Client._query_api') as query_api:
        query_api.side_effect = raise_exception
        yield
