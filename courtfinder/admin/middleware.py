from inspect import getmodule
from django.conf import settings
from django.shortcuts import redirect
import views as admin_views


class RequireLoginMiddleware:
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Restrict every view in admin module, so they don't have to be
        wrapped in @login_required decorator
        """
        if getmodule(view_func) is admin_views and not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)
