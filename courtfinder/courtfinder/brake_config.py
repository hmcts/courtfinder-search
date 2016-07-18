from brake.backends import cachebe


class ELBBrake(cachebe.CacheBackend):
    def get_ip(self, request):
        return request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR'))
