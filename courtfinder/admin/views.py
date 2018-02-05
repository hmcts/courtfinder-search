from django.shortcuts import render, redirect
from search.models import Court, CourtAddress
from django.contrib.auth.models import User
from forms import CourtBasicForm, CourtAddressForm
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from collections import OrderedDict as odict
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

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


def edit_address(request, id, address_id=None):
    court = get_object_or_404(Court, pk=id)
    if request.POST:
        form_index = int(request.POST["form_index"])
        if address_id:
            try:
                court_address = CourtAddress.objects.get(pk=address_id)
            except CourtAddress.DoesNotExist:
                court_address = None
        else:
            court_address = None
        form = CourtAddressForm(data=request.POST or None, address_index=form_index, court=court, instance=court_address)
        if form.is_valid():
            court_address = form.save(commit=False)
            court_address.court = court
            court_address.save()
        return HttpResponseRedirect(reverse("admin:address", args=(id, )))
    else:
        court_addresses = court.courtaddress_set.all().order_by('pk')
        court_address_forms = odict()
        for i, c in enumerate(court_addresses):
            c_address_form = CourtAddressForm(instance=c, address_index=i, court=court)
            court_address_forms[c_address_form] = c.pk
        while len(court_address_forms) < 2:
            new_address = CourtAddressForm(instance=None, address_index=len(court_address_forms), court=court)
            court_address_forms[new_address] = None
        return render(request, 'court_address.jinja', {
            'court': court,
            "court_address_forms": court_address_forms,
        })


def delete_address(request, id, address_id=None):
    court = get_object_or_404(Court, pk=id)
    try:
        court_address = CourtAddress.objects.filter(court=court).get(pk=address_id)
    except CourtAddress.DoesNotExist:
        court_address = None
    if court_address:
        court_address.delete()
    return HttpResponseRedirect(reverse("admin:address", args=(id, )))