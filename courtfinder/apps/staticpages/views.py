import json
import smtplib
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from django.http import Http404
from raven.contrib.django.raven_compat.models import client


def index(request):
    if "court_id" not in request.GET:
        return redirect('search:search')
    else:
        return redirect_old_id_to_slug(request.GET['court_id'])


def api(request, extension=None):
    return render(request, 'staticpages/api.jinja')


def feedback(request):
    return render(request, 'staticpages/feedback.jinja')


class FeedbackForm(forms.Form):
    feedback_text = forms.CharField(label='feedback_text', max_length=200)
    feedback_referer = forms.CharField(label='feedback_referer', max_length=512)
    feedback_email = forms.CharField(label='feedback_email', max_length=2000, required=False)


def feedback_submit(request):
    form = FeedbackForm(request.POST)
    if form.is_valid():
        from_address = settings.FEEDBACK_EMAIL_SENDER
        to_addresses = [address.strip() for address in settings.FEEDBACK_EMAIL_RECEIVER.split(',')]
        if from_address and to_addresses:
            message = """
New feedback has arrived for courtfinder (https://courttribunalfinder.service.gov.uk/).
The user left feedback after seeing: %s
User's browser: %s
User's email: %s

Message: %s
""" % (form.cleaned_data['feedback_referer'],
       request.META.get('HTTP_USER_AGENT', '(unknown)'),
       form.cleaned_data['feedback_email'] or '(not provided)',
       form.cleaned_data['feedback_text'])

            try:
                send_mail('Feedback received for Court and Tribunal Finder',
                          message, from_address,
                          to_addresses, fail_silently=False)
            except smtplib.SMTPException:
                client.captureException()
                # do nothing else in case of error. User doesn't need to see.

    return redirect('staticpages:feedback_sent')


def feedback_sent(request):
    return render(request, 'staticpages/feedback_sent.jinja')


def redirect_old_id_to_slug(old_id):
    ids_file = os.path.join(settings.PROJECT_ROOT, '../data/old_id/ids.json')
    old_ids = json.loads(open(ids_file).read())
    try:
        return redirect('courts:court', slug=old_ids[old_id])
    except KeyError:
        raise Http404()
