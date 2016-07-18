from brake.backends import cachebe


class ELBBrake(cachebe.CacheBackend):
    def get_ip(self, request):

        import pdb; pdb.set_trace()

        try:
            return request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0]
        except (AttributeError, IndexError):
            return request.META.get('REMOTE_ADDR')
