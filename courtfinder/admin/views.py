from django.shortcuts import render, redirect
from search.models import Court
from django.contrib.auth.models import User
from forms import CourtBasicForm
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

def courts(request):
    return render(request, 'courts.jinja', {
        'courts': Court.objects.order_by('name').all()
    })


def users(request):
    return render(request, 'users.jinja', {
        'users': User.objects.order_by('first_name').all()
    })


def edit_court(request, id):
    court = get_object_or_404(Court, pk=id)
    if request.method == 'POST':
        form = CourtBasicForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            # don't allow duplicate names/slugs
            if Court.objects.filter(name=name).exclude(id=id).count():
                form.add_error('name', 'Court with this name already exists')
            else:
                court.update_name_slug(name)
                court.displayed = form.cleaned_data['displayed']
                court.alert = form.cleaned_data['alert']
                court.info = form.cleaned_data['info']
                court.save()
    else:
        form = CourtBasicForm(initial=model_to_dict(court))

    return render(request, 'court_basic.jinja', {
        'court': court,
        'form': form
    })


def edit_address(request,id):
    court = get_object_or_404(Court, pk=id)
    return render(request, 'court_address.jinja', {
        'court': court,
    })
