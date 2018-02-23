from django.shortcuts import render, redirect

from search.models import Court, CourtAddress, Contact, CourtContact, Email, CourtEmail, OpeningTime, CourtOpeningTime, Facility, CourtFacility
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from collections import OrderedDict as odict
from forms import CourtBasicForm, CourtAddressForm, UserAddForm, CourtContactForm, CourtEmailForm, CourtOpeningForm, CourtFacilityForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import modelformset_factory
from django.views import View
import json


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


class BaseOrderableFormView(View):
    template = None
    return_url = None
    reorder_url = None
    formset = None
    objects = None
    court = None
    ordering = True
    update_message = "Updated"

    def get_context_data(self):
        pass

    def process_request(self, request):
        pass

    def initialize(self, request, id):
        self.court = get_object_or_404(Court, pk=id)

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
        return HttpResponseRedirect(self.return_url)


class OrderableFormView(BaseOrderableFormView):
    template = 'court_orderable.jinja'

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
        }
        return context


class ReorderingFormView(BaseOrderableFormView):
    template = 'reordering.jinja'

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
        self.formset = modelformset_factory(Contact, CourtContactForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:contact", kwargs={'id': id})
        self.update_message = 'Contacts updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_contacts", kwargs={'id': id})
        self.objects = self.court.contacts.order_by('sort_order')


class ContactFormView(ContactMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_contact = CourtContact(court=self.court, contact=instance)
                court_contact.save()
            else:
                instance.save()


class ContactReorderView(ContactMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_contact = CourtContact.objects.get(court=self.court, contact=o)
            except CourtContact.DoesNotExist:
                pass
            if court_contact:
                contact = court_contact.contact
                contact.sort_order = i
                contact.save()


class EmailMixin(object):

    def initialize(self, request, id):
        super(EmailMixin, self).initialize(request, id)
        self.formset = modelformset_factory(Email, CourtEmailForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:email", kwargs={'id': id})
        self.update_message = 'Emails updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_emails", kwargs={'id': id})
        self.objects = self.court.emails.order_by('courtemail__order')


class EmailFormView(EmailMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_email = CourtEmail(court=self.court, email=instance)
                court_email.save()
            else:
                instance.save()


class EmailReorderView(EmailMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_email = CourtEmail.objects.get(court=self.court, email=o)
            except CourtEmail.DoesNotExist:
                pass
            if court_email:
                court_email.order = i
                court_email.save()


class OpeningTimeMixin(object):

    def initialize(self, request, id):
        super(OpeningTimeMixin, self).initialize(request, id)
        self.formset = modelformset_factory(OpeningTime, CourtOpeningForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:opening", kwargs={'id': id})
        self.update_message = 'Opening times updated'

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_openings", kwargs={'id': id})
        self.objects = self.court.opening_times.order_by('courtopeningtime__sort')


class OpeningFormView(OpeningTimeMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_opening = CourtOpeningTime(court=self.court, opening_time=instance)
                court_opening.save()
            else:
                instance.save()


class OpeningReorderView(OpeningTimeMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_opening = CourtOpeningTime.objects.get(court=self.court, opening_time=o)
            except CourtEmail.DoesNotExist:
                pass
            if court_opening:
                court_opening.sort = i
                court_opening.save()
                
                
class FacilityMixin(object):

    def initialize(self, request, id):
        super(FacilityMixin, self).initialize(request, id)
        self.formset = modelformset_factory(Facility, CourtFacilityForm, extra=1, can_delete=True)
        self.return_url = reverse("admin:facility", kwargs={'id': id})
        self.update_message = 'Facilities updated'
        self.ordering = False

    def initialize_get(self, request, id):
        self.initialize(request, id)
        self.reorder_url = reverse("admin:reorder_facilities", kwargs={'id': id})
        self.objects = self.court.facilities.all()


class FacilityFormView(FacilityMixin, OrderableFormView):

    def handle_instance_saving(self, instances):
        for instance in instances:
            if instance._state.adding:
                instance.save()
                court_facility = CourtFacility(court=self.court, facility=instance)
                court_facility.save()
            else:
                instance.save()


class FacilityReorderView(FacilityMixin, ReorderingFormView):

    def update_order(self, new_order):
        new_order = json.loads(new_order)
        for i, o in enumerate(new_order):
            try:
                court_facility = CourtFacility.objects.get(court=self.court, facility=o)
            except CourtEmail.DoesNotExist:
                pass
            if court_facility:
                court_facility.save()