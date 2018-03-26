from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.text import slugify
from search import models
from .models import FacilityType


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name= forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ('username', 'is_superuser', 'first_name', 'last_name', 'email')
        labels = {'is_superuser': 'Super admin'}


class UserAddForm(UserEditForm, UserCreationForm):
    pass


class UserDeleteForm(forms.Form):
    username = UsernameField(required=True)


class EmergencyMessageForm(forms.ModelForm):
    class Meta:
        model = models.EmergencyMessage
        fields = ('show', 'message')
        labels = {'show': 'Show on home page'}
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6, 'class': 'rich-editor'})
        }


class CourtNewForm(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ('name',)

    def clean_name(self):
        name = self.cleaned_data['name']
        if not len(slugify(name)):
            raise forms.ValidationError('This name cannot be turned into a valid url')
        courts = models.Court.objects.filter(slug=slugify(name))
        if self.instance:
            courts = courts.exclude(id=self.instance.id)
        if courts.count():
            raise forms.ValidationError('Court with this name already exists')
        return name

    def save(self, commit=True):
        self.instance.slug = slugify(self.instance.name)
        return super(forms.ModelForm, self).save(self)


class CourtBasicForm(CourtNewForm, forms.ModelForm):
    def __init__(self, data, court, extra_perms):
        super(CourtBasicForm, self).__init__(data if data else None, instance=court)
        if not extra_perms:
            self.fields['info'].disabled = True

    class Meta:
        model = models.Court
        fields = ('name', 'alert', 'info', 'displayed')
        labels = {'alert': 'Urgent notice', 'displayed': 'Open', 'info': 'Additional information'}
        widgets = {
            'alert': forms.Textarea(attrs={'rows': 3}),
            'info': forms.Textarea(attrs={'rows': 6, 'class': 'rich-editor'})
        }
        help_texts = {
            'alert': 'Use this field to display a temporary notice of building closure or \
            temporary disruption to court services. This is limited to 250 characters including spaces.'
        }


class CourtLocationForm(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ('directions', 'lat', 'lon')
        labels = {'directions': 'Local Information', 'lat': 'Latitude', 'lon': 'Longitude'}
        widgets = {'directions': forms.Textarea(attrs={'rows': 4})}


class CourtLeafletsForm(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ('info_leaflet', 'defence_leaflet', 'prosecution_leaflet', 'juror_leaflet')
        widgets = {
            'info_leaflet': forms.Textarea(attrs={'rows': 6}),
            'defence_leaflet': forms.Textarea(attrs={'rows': 6}),
            'prosecution_leaflet': forms.Textarea(attrs={'rows': 6}),
            'juror_leaflet': forms.Textarea(attrs={'rows': 6}),
        }
        labels = {
            'info_leaflet': 'Information leaflet',
            'prosecution_leaflet': 'Prosecution witness leaflet',
            'defence_leaflet': 'Defence witness leaflet',
        }


class LocatePostcodeForm(forms.Form):
    postcode = forms.CharField(max_length=9)


class CourtAddressForm(forms.ModelForm):
    class Meta:
        model = models.CourtAddress
        fields = ['address_type', 'address', 'town', 'postcode']

    def __init__(self, address_index=None, court=None, *args, **kwargs):
        super(CourtAddressForm, self).__init__(*args, **kwargs)
        address_types = models.AddressType.objects.all()
        self.fields['town'].queryset = models.Town.objects.all().order_by('name')
        if address_index and address_index > 0:
            address_types = address_types.exclude(name="Visit us or write to us")
            if court:
                primary_address = court.primary_address()
                if primary_address:
                    primary_address_type = primary_address.address_type
                    if not primary_address_type.name == "Visit us or write to us":
                        address_types = address_types.exclude(name=primary_address_type.name)
                    else:
                        address_types = models.AddressType.objects.none()
        if hasattr(self.instance, 'address_type'):
            if self.instance.address_type not in address_types:
                self.fields["address"].disabled = True
                self.fields["postcode"].disabled = True
                self.fields["town"].disabled = True
        self.fields['address_type'].queryset = address_types


class CourtContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = ['name', 'number', 'explanation', 'in_leaflet', 'sort_order']

    def __init__(self, *args, **kwargs):
        super(CourtContactForm, self).__init__(*args, **kwargs)
        self.fields["explanation"].required = False
        self.fields['sort_order'].widget = forms.HiddenInput()
        self.fields['sort_order'].required = False


class CourtEmailForm(forms.ModelForm):
    class Meta:
        model = models.Email
        fields = ['description', 'address']


class CourtOpeningForm(forms.ModelForm):
    class Meta:
        model = models.OpeningTime
        fields = ['description']


class CourtFacilityForm(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=FacilityType.objects.all().distinct('name'), required=True,
                                  to_field_name='name')

    class Meta:
        model = models.Facility
        fields = ['name', 'description', 'image', 'image_description', 'image_file_path']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'class': 'rich-editor'}),
            'image': forms.HiddenInput(),
            'image_description': forms.HiddenInput(),
            'image_file_path': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CourtFacilityForm, self).__init__(*args, **kwargs)
        is_new_instance = self.instance._state.adding
        if not is_new_instance:
            try:
                self.initial["name"] = FacilityType.objects.filter(name=self.instance.name).first()
            except FacilityType.DoesNotExist:
                print "Facility type not found"

    def save(self, *args, **kwargs):
        fac_form = super(CourtFacilityForm, self).save(*args, **kwargs)
        fac_type = FacilityType.objects.filter(name=self.instance.name).first()
        fac_form.name = fac_type.name
        fac_form.image_description = fac_type.image_description
        fac_form.image_file_path = fac_type.image_file_path
        return fac_form


class CourtAreasOfLawForm(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ['areas_of_law', 'hide_aols']
        widgets = {
            'areas_of_law': forms.CheckboxSelectMultiple()
        }
        labels = {'hide_aols': "Hide 'Cases heard at this venue'"}

    def _save_m2m(self):
        selection = self.cleaned_data['areas_of_law']
        mngr = models.CourtAreaOfLaw.objects
        mngr.filter(court=self.instance).exclude(area_of_law__in=selection).delete()
        for aol in self.cleaned_data['areas_of_law']:
            mngr.get_or_create(court=self.instance, area_of_law=aol)


class CourtTypes(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ['court_types', 'number', 'cci_code', 'magistrate_code']
        widgets = {
            'court_types': forms.CheckboxSelectMultiple()
        }
        labels = {
            'number': 'Crown Court code',
            'cci_code': 'County Court code',
            'magistrate_code': "Magistrates' Court code",
        }

    def _save_m2m(self):
        # todo remove intermiediete model so this is isn't necessary?
        mngr = models.CourtCourtType.objects
        mngr.filter(court=self.instance).delete()
        for type in self.cleaned_data['court_types']:
            mngr.create(court=self.instance, court_type=type)


class UploadPhotoForm(forms.Form):
    image = forms.ImageField()
