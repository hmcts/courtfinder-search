from django.shortcuts import render, redirect

from search.models import Court, CourtAddress, Contact, CourtContact
from django.contrib.auth.models import User
from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from collections import OrderedDict as odict
from forms import CourtBasicForm, CourtAddressForm, UserAddForm, CourtContactForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import modelformset_factory

def courts(request):
    return render(request, 'courts.jinja', {
        'courts': Court.objects.order_by('name').all()
    })


def users(request):
    return render(request, 'users.jinja', {
        'users': User.objects.order_by('first_name').all()
    })


def add_user(request):
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, '`%s` has been added' % new_user.username)
            return HttpResponseRedirect(reverse('admin:users'))
    else:
        form = UserAddForm()

    return render(request, 'add_user.jinja', {
        'form': form
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
                messages.success(request, 'Court information updated')
                return HttpResponseRedirect(reverse("admin:court", args=(id,)))
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
            messages.success(request, 'Address updated')
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
        messages.success(request, 'Address deleted')
    return HttpResponseRedirect(reverse("admin:address", args=(id, )))


def edit_contact(request, id):
    court = get_object_or_404(Court, pk=id)
    contact_formset = modelformset_factory(Contact, CourtContactForm, extra=1, can_delete=True)

    if request.POST:
        formset = contact_formset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for instance in instances:
                if instance._state.adding:
                    instance.save()
                    court_contact = CourtContact(court=court, contact=instance)
                    court_contact.save()
                else:
                    instance.save()
            messages.success(request, 'Contacts updated')
        return HttpResponseRedirect(reverse("admin:contact", args=(id, )))
    court_contact_queryset = court.contacts.order_by('sort_order')
    formset = contact_formset(queryset=court_contact_queryset)
    return render(request, 'court_contacts.jinja', {
            'court': court,
            "formset": formset,
        })


def reorder_contacts(request, id):
    import json
    court = get_object_or_404(Court, pk=id)
    return_url = reverse("admin:contact", kwargs={'id': id})
    reorder_url = reverse("admin:reorder_contacts", kwargs={'id': id})
    if request.POST:
        if "new_sort_order" in request.POST:
            new_order = request.POST["new_sort_order"]
            if new_order:
                new_order = json.loads(new_order)
                for i, o in enumerate(new_order):
                    try:
                        court_contact = CourtContact.objects.get(court=court, contact=o)
                    except CourtContact.DoesNotExist:
                        pass
                    if court_contact:
                        contact = court_contact.contact
                        contact.sort_order = i
                        contact.save()
        return HttpResponseRedirect(reverse("admin:contact", args=(id, )))
    contacts = court.contacts.order_by('sort_order')

    return render(request, 'reordering.jinja', {
        'court': court,
        "objects": contacts,
        "return_url": return_url,
        "reorder_url": reorder_url,
        })
