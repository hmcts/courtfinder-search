from ratelimit.decorators import ratelimit
from django.contrib.auth.views import LoginView
from django.shortcuts import render

class ThrottledLoginView(LoginView):
    @ratelimit(key='post:username', rate='10/h', method=['POST'], block=True)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def limited(request, exception):
    return render(request, 'ratelimit.html')
