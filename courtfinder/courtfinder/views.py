from django.conf import settings
from django import http
from django.utils.http import is_safe_url
from django.utils.translation import check_for_language


def set_language(request):
    next = request.GET.get('next')
    if not is_safe_url(url=next, allowed_hosts=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, allowed_hosts=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)

    lang_code = request.GET.get('lang')
    if lang_code and check_for_language(lang_code):
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    return response


def cy_redirect(request):
    response = http.HttpResponseRedirect(request.get_full_path()[3:])
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, 'cy')
    return response
