import json
import smtplib
import logging
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.utils.translation import get_language_from_request
from brake.decorators import ratelimit

from .forms import FeedbackForm

logger = logging.getLogger(__name__)


EMAIL_MESSAGE = """
New feedback has arrived for courtfinder (https://courttribunalfinder.service.gov.uk/).
The user left feedback after seeing: {}
User's browser: {}
User's email: {}

Message: {}
"""


def index(request):
    if "court_id" not in request.GET:
        return redirect('search:search')
    else:
        return redirect_old_id_to_slug(request.GET['court_id'])


def feedback(request):
    return render(request, 'staticpages/feedback.jinja')


feedback_receiver_languages = {"en": settings.FEEDBACK_EMAIL_RECEIVER,
                               "cy": settings.WELSH_FEEDBACK_EMAIL_RECEIVER}


@ratelimit(rate='3/h')
def feedback_submit(request):
    form = FeedbackForm(request.POST)

    rate_limited = getattr(request, 'limited', False)
    if form.is_valid() and not rate_limited:
        from_address = settings.FEEDBACK_EMAIL_SENDER
        to_addresses = [address.strip() for address in feedback_receiver_languages[get_language_from_request(request)]
                        .split(',')]
        if from_address and to_addresses:
            feedback_email = form.cleaned_data['feedback_email']

            if not feedback_email:
                feedback_email = "(no email supplied)"

            message = EMAIL_MESSAGE.format(
                form.cleaned_data['feedback_referer'],
                request.META.get('HTTP_USER_AGENT','(unknown)'),
                feedback_email,
                form.cleaned_data['feedback_text'])
            try:
                send_mail('Feedback received for Court and Tribunal Finder',
                          message, from_address,
                          to_addresses, fail_silently=False)
            except smtplib.SMTPException as e:
                logger.error(e)

    return redirect('staticpages:feedback_sent')


def feedback_sent(request):
    return render(request, 'staticpages/feedback_sent.jinja')


def redirect_old_id_to_slug(old_id):
    ids_file = settings.PROJECT_ROOT + '/data/old_id/ids.json'
    old_ids = json.loads(open(ids_file).read())
    try:
        return redirect('courts:court', slug=old_ids[old_id])
    except KeyError:
        raise Http404()
