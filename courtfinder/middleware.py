import json
import logging
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
                'responseCode': getattr(response, 'status_code', 0),
                'responseTime': time() - self.request_time,
                'time': strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                'fullPath': request.get_full_path(),
                'path': request.path,
                'method': request.method,
                'get': request.GET,
                'post': request.POST,
                'userAgent': request.META['HTTP_USER_AGENT'],
                'ipAddress': request.META['REMOTE_ADDR'],
            }))
        except:
            pass

        return response
