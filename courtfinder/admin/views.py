import forms
import json
from collections import OrderedDict as odict
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from geolocation import mapit
from search import models
from django.views import View


@permission_required('emergency')
def emergency_message(request):
    msg = models.EmergencyMessage.objects.all().first()
    if request.method == 'POST':
        form = forms.EmergencyMessageForm(request.POST, instance=msg)
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency message updated')
            messages.warning(request, 'The message is now *%s*' % ('visible' if msg.show else 'hidden'))
            return redirect('admin:emergency')
    else:
        form = forms.EmergencyMessageForm(instance=msg)

    return render(request, 'emergency.html', {
        'form': form
    })


def courts(request):
    return render(request, 'court/list.html', {
        'courts': models.Court.objects.order_by('name').all()
    })


@permission_required('user.manage')
def users(request):
    return render(request, 'user/list.html', {
        'users': User.objects.order_by('username').all()
    })


@permission_required('user.manage')
def add_user(request):
    if request.method == 'POST':
        form = forms.UserAddForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, '`%s` has been added' % new_user.username)
            return redirect('admin:users')
    else:
        form = forms.UserAddForm()

    return render(request, 'user/add.html', {
        'form': form
    })


@permission_required('user.manage')
def edit_user(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = forms.UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '`%s` has been updated' % user.username)
            return redirect('admin:edit_user', user.username)
    else:
        form = forms.UserEditForm(instance=user)

    return render(request, 'user/edit.html', {
        'username': user.username,
        'form': form,
        'delete_form': forms.UserDeleteForm()
    })


@permission_required('user.manage')
def change_user_password(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '`%s` password has been updated' % user.username)
            return redirect('admin:edit_user', user.username)
    else:
        form = AdminPasswordChangeForm(user)

    return render(request, 'user/password.html', {
        'form': form,
        'username': user.username,
    })


@require_POST
@permission_required('user.manage')
def delete_user(request, username):
    form = forms.UserDeleteForm(request.POST)
    if form.is_valid() and form.cleaned_data['username'] == username:
        user = get_object_or_404(User, username=username)
        user.delete()
        messages.success(request, '`%s` has been deleted' % username)
        return redirect('admin:users')
    else:
        messages.error(request, 'Could\'t delete user `%s`' % username)
        return redirect('admin:edit_user', username)


def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'account.html', {
        'form': form
    })


@permission_required('court.new')
def new_court(request):
    form = forms.CourtNewForm(request.POST if request.POST else None)
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        if models.Court.objects.filter(name=name).count():
            form.add_error('name', 'Court with this name already exists')
        else:
            court = form.save(commit=False)
            court.update_name_slug(name)
            court.save()
            messages.success(request, 'New court has been added')
            return redirect('admin:court', court.id)
    return render(request, 'court/new.html', {
        'form': form
    })


def edit_court(request, id):
    court = get_object_or_404(models.Court, pk=id)
    form = forms.CourtBasicForm(request.POST, court, request.user.has_perm('court.info'))
    if request.method == 'POST' and form.is_valid():
        name = form.cleaned_data['name']
        if models.Court.objects.filter(name=name).exclude(id=id).count():
            form.add_error('name', 'Court with this name already exists')
        else:
            form.save(commit=False)
            court.update_name_slug(name)
            court.save()
            messages.success(request, 'Court information updated')
            court.update_timestamp()
            return redirect('admin:court', id)
    return render(request, 'court/basic.html', {
        'court': court,
        'form': form
    })


def edit_location(request, id):
    court = get_object_or_404(models.Court, pk=id)
    if request.method == 'POST':
        form = forms.CourtLocationForm(request.POST, instance=court)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location details updated')
            court.update_timestamp()
            return redirect('admin:location', id)
    else:
        form = forms.CourtLocationForm(instance=court)

    return render(request, 'court/location.html', {
        'court': court,
        'form': form,
        'postcode_form': forms.LocatePostcodeForm()
    })


@require_POST
def locate_postcode(request, id):
    court = get_object_or_404(models.Court, pk=id)
    form = forms.LocatePostcodeForm(request.POST)
    if form.is_valid():
        try:
            postcode = mapit.postcode(form.cleaned_data['postcode'])
            court.lat, court.lon = postcode.coordinates
            court.save()
            messages.success(request, 'Coordinates changed to %s, %s' % (court.lat, court.lon))
            court.update_timestamp()
        except mapit.MapitException as e:
            messages.error(request, 'Geolocation failed: %s' % e.message)
    else:
        messages.error(request, 'Geolocation failed')
    return redirect('admin:location', id)


def edit_address(request, id, address_id=None):
    court = get_object_or_404(models.Court, pk=id)
    if request.POST:
        form_index = int(request.POST["form_index"])
        if address_id:
            try:
                court_address = models.CourtAddress.objects.get(pk=address_id)
            except models.CourtAddress.DoesNotExist:
                court_address = None
        else:
            court_address = None
        form = forms.CourtAddressForm(data=request.POST or None, address_index=form_index, court=court, instance=court_address)
        if form.is_valid():
            court_address = form.save(commit=False)
            court_address.court = court
            court_address.save()
            messages.success(request, 'Address updated')
            court.update_timestamp()
        return redirect('admin:address', id)
    else:
        court_addresses = court.courtaddress_set.all().order_by('pk')
        court_address_forms = odict()
        for i, c in enumerate(court_addresses):
            c_address_form = forms.CourtAddressForm(instance=c, address_index=i, court=court)
            court_address_forms[c_address_form] = c.pk
        while len(court_address_forms) < 2:
            new_address = forms.CourtAddressForm(instance=None, address_index=len(court_address_forms), court=court)
            court_address_forms[new_address] = None
        return render(request, 'court/address.html', {
            'court': court,
            "court_address_forms": court_address_forms,
        })


@require_POST
def delete_address(request, id, address_id=None):
    court = get_object_or_404(models.Court, pk=id)
    try:
        court_address = models.CourtAddress.objects.filter(court=court).get(pk=address_id)
    except models.CourtAddress.DoesNotExist:
        court_address = None
    if court_address:
        court_address.delete()
        messages.success(request, 'Address deleted')
        court.update_timestamp()
    return redirect('admin:address', id)


class BaseOrderableFormView(View):
    template = None
    return_url = None
    reorder_url = None
    formset = None
    objects = None
    court = None
    ordering = True
    update_message = "Updated"
    heading = ""
    header_message = ""

    def get_context_data(self):
        pass

    def process_request(self, request):
        pass

    def initialize(self, request, id):
        self.court = get_object_or_404(models.Court, pk=id)

    def initialize_get(self, request, id):
        pass

    def get(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        self.initialize_get(request, id)
        return render(request, self.template, self.get_context_data())

    def post(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        self.initialize(request, id)
        self.process_request(request)
        return redirect(self.return_url)


class OrderableFormView(BaseOrderableFormView):
    template = 'court/orderable.html'

    def handle_instance_saving(self, instances):
        pass

    def process_request(self, request):
        formset = self.formset(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            self.handle_instance_saving(instances)
            messages.success(request, self.update_message)

    def get_context_data(self):
        formset = self.formset(queryset=self.objects)
        context = {
            'court': self.court,
            "formset": formset,
            "return_url": self.return_url,
            "reorder_url": self.reorder_url,
            "ordering": self.ordering,
            'heading': self.heading,
            'header_message': self.header_message,
        }
        return context


class ReorderingFormView(BaseOrderableFormView):
    template = 'court/reordering.html'

    def update_order(self, new_order):
        pass

    def process_request(self, request):
        if "new_sort_order" in request.POST:
            new_order = request.POST["new_sort_order"]
            if new_order:
                self.update_order(new_order)

    def get_context_data(self):
        context = {
            'court': self.court,
            "objects": self.objects,
            "return_url": self.return_url,
            "reorder_url": self.reorder_url,
            }
        return context


class ContactMixin(object):

    def initialize(self, request, id):
        super(ContactMixin, self).initialize(request, id)
        self.formset = modelformset_factory(models.Contact, forms.CourtContactForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:contact", kwargs={'id': id})
        self.update_message = 'Contacts updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_contacts", kwargs={'id': id})
        self.objects = self.court.contacts.order_by('sort_order')
        self.heading = "Edit contacts"
        self.header_message = "The DX contact will show separately in the court header"

class ContactFormView(ContactMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                inst = instance.save()
                instance.sort_order = inst  # Sets the order of the new object to its id to preserve order
                instance.save(update_fields=["sort_order"])
                court_contact = models.CourtContact(court=self.court, contact=instance)
                court_contact.save()
            else:
                instance.save()


class ContactReorderView(ContactMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_contact = models.CourtContact.objects.get(court=self.court, contact=o)
            except models.CourtContact.DoesNotExist:
                pass
            if court_contact:
                contact = court_contact.contact
                contact.sort_order = i
                contact.save()


class EmailMixin(object):

    def initialize(self, request, id):
        super(EmailMixin, self).initialize(request, id)
        self.formset = modelformset_factory(models.Email, forms.CourtEmailForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:email", kwargs={'id': id})
        self.update_message = 'Emails updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_emails", kwargs={'id': id})
        self.objects = self.court.emails.order_by('courtemail__order')
        self.heading = "Edit email addresses"


class EmailFormView(EmailMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_email = models.CourtEmail(court=self.court, email=instance)
                court_email.save()
                court_email.order = court_email.pk  # Sets the order of the new object to its id to preserve order
                court_email.save(update_fields=["order"])
            else:
                instance.save()


class EmailReorderView(EmailMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_email = models.CourtEmail.objects.get(court=self.court, email=o)
            except CourtEmail.DoesNotExist:
                pass
            if court_email:
                court_email.order = i
                court_email.save()


class OpeningTimeMixin(object):

    def initialize(self, request, id):
        super(OpeningTimeMixin, self).initialize(request, id)
        self.formset = modelformset_factory(models.OpeningTime, forms.CourtOpeningForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:opening", kwargs={'id': id})
        self.update_message = 'Opening times updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_openings", kwargs={'id': id})
        self.objects = self.court.opening_times.order_by('courtopeningtime__sort')
        self.heading = "Edit opening times"


class OpeningFormView(OpeningTimeMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_opening = models.CourtOpeningTime(court=self.court, opening_time=instance)
                court_opening.save()
                court_opening.sort = court_opening.pk  # Sets the order of the new object to its id to preserve order
                court_opening.save(update_fields=["sort"])
            else:
                instance.save()


class OpeningReorderView(OpeningTimeMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_opening = models.CourtOpeningTime.objects.get(court=self.court, opening_time=o)
            except models.CourtEmail.DoesNotExist:
                pass
            if court_opening:
                court_opening.sort = i
                court_opening.save()
                
                
class FacilityMixin(object):

    def initialize(self, request, id):
        super(FacilityMixin, self).initialize(request, id)
        self.formset = modelformset_factory(models.Facility, forms.CourtFacilityForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:facility", kwargs={'id': id})
        self.update_message = 'Facilities updated'
        self.ordering = False

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_facilities", kwargs={'id': id})
        self.objects = self.court.facilities.all()
        self.heading = "Edit facilities"


class FacilityFormView(FacilityMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_facility = models.CourtFacility(court=self.court, facility=instance)
                court_facility.save()
            else:
                instance.save()


class FacilityReorderView(FacilityMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_facility = models.CourtFacility.objects.get(court=self.court, facility=o)
            except models.CourtEmail.DoesNotExist:
                pass
            if court_facility:
                court_facility.save()


def areas_of_law(request, id):
    court = get_object_or_404(models.Court, pk=id)
    form = forms.CourtAreasOfLawForm(request.POST if request.POST else None, instance=court)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Areas of law updated')
        court.update_timestamp()
        return redirect('admin:aols', court.id)

    return render(request, 'court/aols.html', {
        'form': form,
        'court': court,
    })
