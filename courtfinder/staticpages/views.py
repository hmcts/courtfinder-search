from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django import forms

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
    feedback_email = forms.CharField(label='feedback_email', max_length=2000, required=False)

def feedback_sent(request):
    form = FeedbackForm(request.POST)
    if form.is_valid():
        from_address = settings.FEEDBACK_EMAIL_SENDER
        to_addresses = [address.strip() for address in settings.FEEDBACK_EMAIL_RECEIVER.split(',')]
        if from_address and to_addresses:
            message = """New feedback has arrived for courtfinder.
Sender: %s

Message: %s""" % (form.cleaned_data['feedback_email'],
                  form.cleaned_data['feedback_text'])

            nb_emails_sent = send_mail('Feedback for courtfinder',
                                       message, from_address,
                                       to_addresses, fail_silently=False)

    return render(request, 'staticpages/feedback_sent.jinja')
