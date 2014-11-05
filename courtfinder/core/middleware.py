import json
import logging
from syslog import syslog
from time import gmtime, strftime

from django.http import Http404

import pprint

pp = pprint.PrettyPrinter(indent=4)

class RequestLoggingMiddleware(object):

    def __init__(self):
        self.logger = logging.getLogger('courtfinder.requests')

    def process_request(self, request):
        self.logger.debug(json.dumps({
            'time': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            'fullPath': request.get_full_path(),
            'path': request.path,
            'method': request.method,
            'get': request.GET,
            'post': request.POST,
            'userAgent': request.META['HTTP_USER_AGENT'],
            'ipAddress': request.META['REMOTE_ADDR'],
        }))
