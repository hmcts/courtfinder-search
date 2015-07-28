from django.http import QueryDict


def updated_query_string(query_dict, **replacements):
    """
    Takes a QueryDict, like requests.GET, and replaces parameters from `replacements`
    :returns: updated query string
    """
    updated_parameters = QueryDict('', mutable=True)
    updated_parameters.update(query_dict)
    for key, value in replacements.items():
        updated_parameters[key] = value
    return updated_parameters.urlencode()
