from django.shortcuts import render, redirect

from search.models import Court, CourtAddress, Contact, CourtContact
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from collections import OrderedDict as odict
from forms import *
from geolocation import mapit
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import modelformset_factory
from django.views.decorators.http import require_POST


def courts(request):
    return render(request, 'courts.jinja', {
        'courts': Court.objects.order_by('name').all()
    })


@permission_required('manage_users')
def users(request):
    return render(request, 'users.jinja', {
        'users': User.objects.order_by('username').all()
    })


@permission_required('manage_users')
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


@permission_required('manage_users')
def edit_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '`%s` has been updated' % user.username)
            return HttpResponseRedirect(reverse('admin:edit_user', args=(user.username,)))
    else:
        form = UserEditForm(instance=user)

    return render(request, 'user/edit.html', {
        'username': user.username,
        'form': form,
        'delete_form': UserDeleteForm()
    })


@permission_required('manage_users')
def change_user_password(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '`%s` password has been updated' % user.username)
            return HttpResponseRedirect(reverse('admin:edit_user', args=(user.username,)))
    else:
        form = AdminPasswordChangeForm(user)

    return render(request, 'user/password.html', {
        'form': form,
        'username': user.username,
    })


@require_POST
@permission_required('manage_users')
def delete_user(request, username):
    form = UserDeleteForm(request.POST)
    if form.is_valid() and form.cleaned_data['username'] == username:
        user = get_object_or_404(User, username=username)
        user.delete()
        messages.success(request, '`%s` has been deleted' % username)
        return HttpResponseRedirect(reverse('admin:users'))
    else:
        messages.error(request, 'Could\'t delete user `%s`' % username)
        return HttpResponseRedirect(reverse('admin:edit_user', args=(username,)))


def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account.jinja', {
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


def edit_location(request, id):
    court = get_object_or_404(Court, pk=id)
    if request.method == 'POST':
        form = CourtLocationForm(request.POST, instance=court)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location details updated')
            return HttpResponseRedirect(reverse("admin:location", args=(id,)))
    else:
        form = CourtLocationForm(instance=court)

    return render(request, 'court_location.jinja', {
        'court': court,
        'form': form,
        'postcode_form': LocatePostcodeForm()
    })


@require_POST
def locate_postcode(request, id):
    court = get_object_or_404(Court, pk=id)
    form = LocatePostcodeForm(request.POST)
    if form.is_valid():
        try:
            postcode = mapit.postcode(form.cleaned_data['postcode'])
            court.lat, court.lon = postcode.coordinates
            court.save()
            messages.success(request, 'Coordinates changed to %s, %s' % (court.lat, court.lon))
        except mapit.MapitException as e:
            messages.error(request, 'Geolocation failed: %s' % e.message)
    else:
        messages.error(request, 'Geolocation failed')
    return HttpResponseRedirect(reverse("admin:location", args=(id,)))


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
