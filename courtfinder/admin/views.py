from django.shortcuts import render, redirect
from search.models import Court
from django.contrib.auth.models import User


def courts(request):
    return render(request, 'courts.jinja')


def users(request):
    return render(request, 'users.jinja', {
        'users': User.objects.order_by('first_name').all()
    })


def edit(request, slug):
    return render(request, 'edit.jinja', {
        'court': Court.objects.get(slug=slug)
    })
