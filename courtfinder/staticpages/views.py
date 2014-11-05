from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django import forms
from raven.contrib.django.raven_compat.models import client

def index(request):
    return render(request, 'staticpages/index.jinja')

def api(request, extension=None):
    return render(request, 'staticpages/api.jinja')

def error(request):
    return render(request, 'staticpages/error.jinja')

def notfound(request):
    return render(request, 'staticpages/notfound.jinja')

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
            feedback_email = form.cleaned_data['feedback_email']
            if not feedback_email:
                feedback_email = '(not provided)'
            message = """
New feedback has arrived for courtfinder (https://courttribunalfinder.service.gov.uk/).
The user left feedback after seeing: %s
User's browser: %s
User's email: %s

Message: %s
""" % (form.cleaned_data['feedback_referer'],
       request.META.get('HTTP_USER_AGENT','(unknown)'),
       form.cleaned_data['feedback_email'],
       form.cleaned_data['feedback_text'])

        try:
            nb_emails_sent = send_mail('Feedback received for Court and Tribunal Finder',
                                       message, from_address,
                                       to_addresses, fail_silently=False)
        except smtplib.SMTPException:
            client.captureException()
            # do nothing else in case of error. User doesn't need to see.


    return redirect(reverse('staticpages:feedback_sent'))

def feedback_sent(request):
    return render(request, 'staticpages/feedback_sent.jinja')
