from django.shortcuts import render, redirect
from search.models import Court
from django.contrib.auth.models import User


def courts(request):
    return render(request, 'courts.jinja', {
        'courts': Court.objects.order_by('name').all()
    })


def users(request):
    return render(request, 'users.jinja', {
        'users': User.objects.order_by('first_name').all()
    })


def court(request, id):
    return render(request, 'court.jinja', {
        'court': Court.objects.get(id=id)
    })
