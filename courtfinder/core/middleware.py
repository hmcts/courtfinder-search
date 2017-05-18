import json
import logging
from syslog import syslog
from time import gmtime, strftime, time

import pprint

pp = pprint.PrettyPrinter(indent=4)

class RequestLoggingMiddleware(object):
    def process_request(self, request):
        self.logger = logging.getLogger('courtfinder.requests')
        self.request_time = time()

    def process_response(self, request, response):
        try:
            self.logger.debug(json.dumps({
                '@fields': {
                    'status': getattr(response, 'status_code', 0),
                    'request_time': time() - self.request_time,
                    'remote_addr': request.META['REMOTE_ADDR'],
                    'http_user_agent': request.META['HTTP_USER_AGENT'],
                    'request_uri': request.get_full_path(),
                },
                'fullPath': request.get_full_path(),
                'path': request.path,
                'get': request.GET,
                'post': request.POST,
            }))
        except:
            pass

        return response

