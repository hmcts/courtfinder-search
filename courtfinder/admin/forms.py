from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.text import slugify
from search import models
from .models import FacilityType, ContactType, OpeningType
import re
import urllib


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
        fields = ('name', 'displayed', 'alert', 'info')
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

    def clean_lat(self):
        data = self.cleaned_data['lat']
        if not re.match('^(\+|-)?((\d((\.)|\.\d+)?)|(0*?[0-8]\d((\.)|\.\d+)?)|(0*?90((\.)|\.0+)?))$', str(data)):
            raise forms.ValidationError('Invalid latitude')
        return data

    def clean_lon(self):
        data = self.cleaned_data['lon']
        if not re.match('^(\+|-)?((\d((\.)|\.\d+)?)|(0*?\d\d((\.)|\.\d+)?)|(0*?1[0-7]\d((\.)|\.\d+)?)|(0*?180((\.)|\.0+)?))$', str(data)):
            raise forms.ValidationError('Invalid longitude')
        return data


class CourtLeafletsForm(forms.ModelForm):
    class Meta:
        model = models.Court
        fields = ('info_leaflet', 'defence_leaflet', 'prosecution_leaflet',)
        widgets = {
            'info_leaflet': forms.Textarea(attrs={'rows': 6}),
            'defence_leaflet': forms.Textarea(attrs={'rows': 6}),
            'prosecution_leaflet': forms.Textarea(attrs={'rows': 6}),
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
    name = forms.ModelChoiceField(queryset=ContactType.objects.all().distinct('name'), required=True,
                                  to_field_name='name')

    class Meta:
        model = models.Contact
        fields = ['name', 'number', 'explanation', 'in_leaflet', 'sort_order']

    def __init__(self, *args, **kwargs):
        super(CourtContactForm, self).__init__(*args, **kwargs)
        is_new_instance = self.instance._state.adding
        self.fields["number"].required = True
        self.fields["explanation"].required = False
        self.fields['sort_order'].widget = forms.HiddenInput()
        self.fields['sort_order'].required = False
        if not is_new_instance:
            con_type = ContactType.objects.filter(name=self.instance.name).first()
            if con_type:
                self.initial["name"] = con_type
            else:
                self.fields["name"].choices = [("", self.instance.name + " - discontinued type")] + list(self.fields["name"].choices)[1:]
                self.fields["name"].required = False

    def save(self, *args, **kwargs):
        con_form = super(CourtContactForm, self).save(*args, **kwargs)
        con_type = ContactType.objects.filter(name=con_form.name).first()
        if con_type:
            con_form.name = con_type.name
        return con_form


class CourtEmailForm(forms.ModelForm):
    description = forms.ModelChoiceField(queryset=ContactType.objects.all().distinct('name'), required=True,
                                  to_field_name='name')

    class Meta:
        model = models.Email
        fields = ['description', 'address', 'explanation']

    def __init__(self, *args, **kwargs):
        super(CourtEmailForm, self).__init__(*args, **kwargs)
        is_new_instance = self.instance._state.adding
        self.fields["explanation"].required = False
        if not is_new_instance:
            con_type = ContactType.objects.filter(name=self.instance.description).first()
            if con_type:
                self.initial["description"] = con_type.name
            else:
                self.fields["description"].choices = [("", self.instance.description + " - discontinued type")] + list(self.fields["description"].choices)[1:]
                self.fields["description"].required = False

    def save(self, *args, **kwargs):
        con_form = super(CourtEmailForm, self).save(*args, **kwargs)
        con_type = ContactType.objects.filter(name=con_form.description).first()
        if con_type:
            con_form.description = con_type.name
        return con_form


class CourtOpeningForm(forms.ModelForm):

    type = forms.ModelChoiceField(queryset=OpeningType.objects.all().distinct('name'), required=True,
                                  to_field_name='name')
    hours = forms.CharField(required=True, max_length=255)

    class Meta:
        model = models.OpeningTime
        fields = ['description']
        widgets = {
            'description': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CourtOpeningForm, self).__init__(*args, **kwargs)
        is_new_instance = self.instance._state.adding
        if not is_new_instance:
            description_split = self.instance.description.split(':', 1)
            type_name = description_split[0]
            if self.instance.description:
                if len(description_split) > 1:
                    type_hours = description_split[1]
                    type_hours = type_hours[1:]
                else:
                    type_hours = ""
                op_type = OpeningType.objects.filter(name=type_name).first()
            else:
                op_type = None
            if op_type:
                self.initial["type"] = type_name
                self.initial["hours"] = type_hours
            else:
                self.fields["type"].choices = [("", type_name + " - discontinued type")] + list(self.fields["type"].choices)[1:]
                self.fields["type"].required = False
                self.initial["hours"] = type_hours
        else:
            self.initial["type"] = ""
            self.initial["hours"] = ""

    def clean(self, *args, **kwargs):
        cleaned_data = super(CourtOpeningForm, self).clean(*args, **kwargs)
        clean_copy = cleaned_data.copy()
        type_input = clean_copy.get("type", None)
        hours_input = clean_copy.get("hours", None)
        if not type_input:
            return cleaned_data
        if not hours_input:
            raise forms.ValidationError("You must fill in the required fields")
        else:
            op_type = OpeningType.objects.filter(name=type_input).first()
            if op_type:
                clean_copy["description"] = op_type.name + ": " + hours_input
            else:
                clean_copy["description"] = ""
        clean_copy.pop("type")
        clean_copy.pop("hours")
        if self.errors.get("description", None):
            del self.errors["description"]
        self.cleaned_data = clean_copy
        return clean_copy


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
        self.fields["image"].required = False
        self.fields["image_description"].required = False
        if not is_new_instance:
            fac_type = FacilityType.objects.filter(name=self.instance.name).first()
            if fac_type:
                self.initial["name"] = fac_type
            else:
                self.fields["name"].choices = [("", self.instance.name + " - discontinued type")] + list(self.fields["name"].choices)[1:]
                self.fields["name"].required = False

    def save(self, *args, **kwargs):
        fac_form = super(CourtFacilityForm, self).save(*args, **kwargs)
        fac_type = FacilityType.objects.filter(name=fac_form.name).first()
        if fac_type:
            fac_form.name = fac_type.name
            fac_form.image_description = fac_type.image_description
            fac_form.image_file_path = fac_type.image_file_path
        return fac_form

    def clean(self, *args, **kwargs):
        cleaned_data = super(CourtFacilityForm, self).clean(*args, **kwargs)
        description = cleaned_data.get("description", None)
        if not description:
            raise forms.ValidationError("You must fill in the required fields")
        return cleaned_data

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


class FamilyCourtForm(forms.ModelForm):
    local_authorities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = models.CourtAreaOfLaw
        fields = ['single_point_of_entry']

    def __init__(self, data, area, authorities):
        super(FamilyCourtForm, self).__init__(data if data else None, instance=area)
        self.fields['local_authorities'].choices = [
            (a.id, a.name) for a in models.LocalAuthority.objects.order_by('name').all()
        ]
        self.initial['local_authorities'] = [a.local_authority.id for a in authorities]
        self.fields['local_authorities'].required = False

    def save(self, court, area):
        super(FamilyCourtForm, self).save()

        selection = self.cleaned_data['local_authorities']
        mngr = models.CourtLocalAuthorityAreaOfLaw.objects
        mngr.filter(court=court, area_of_law=area).exclude(local_authority__in=selection).delete()
        for authority_id in self.cleaned_data['local_authorities']:
            authority = models.LocalAuthority.objects.get(pk=authority_id)
            mngr.get_or_create(court=court, area_of_law=area, local_authority=authority)


class PostcodesForm(forms.Form):
    postcodes = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label='')
    action = forms.ChoiceField(widget=forms.RadioSelect,
        choices=(('move', 'Move',), ('delete', 'Delete',)), label='')
    destination_court = forms.ChoiceField(widget=forms.Select, required=False,
        help_text="If you're moving postcodes, select destination court from the list")

    def __init__(self, data, postcodes, courts):
        super(PostcodesForm, self).__init__(data if data else None)
        self.fields['postcodes'].choices = [(p.id, p.postcode) for p in postcodes]
        self.fields['destination_court'].choices = [(c.id, c.name) for c in courts]
        self.fields['destination_court'].choices.insert(0, (None, '---'))


class AddPostcodesForm(forms.Form):
    postcodes = forms.CharField(required=True, max_length=300, widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Comma seperated list of postcodes e.g. SA1 1AA, sa12bb. Case and spaces not significant.",
        label='Add postcodes')


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


class UploadImageForm(forms.Form):
    image = forms.ImageField()


class AdminFacilityTypeForm(forms.ModelForm):
    class Meta:
        model = FacilityType
        fields = ['name', 'image_description']


class AdminContactTypeForm(forms.ModelForm):
    class Meta:
        model = ContactType
        fields = ['name']


class AdminOpeningTypeForm(forms.ModelForm):
    class Meta:
        model = OpeningType
        fields = ['name']


class AdminAOLForm(forms.ModelForm):
    class Meta:
        model = models.AreaOfLaw
        fields = ['name', 'external_link', 'external_link_desc']

    def __init__(self, *args, **kwargs):
        super(AdminAOLForm, self).__init__(*args, **kwargs)
        self.fields['name'].disabled = True
        is_new_instance = self.instance._state.adding
        if not is_new_instance:
            if self.instance.external_link:
                self.initial['external_link'] = self.instance.display_url()

    def clean(self, *args, **kwargs):
        cleaned_data = super(AdminAOLForm, self).clean(*args, **kwargs)
        clean_copy = cleaned_data.copy()
        uncoded_url = clean_copy.get('external_link', None)
        if uncoded_url:
            clean_copy['external_link'] = urllib.quote(uncoded_url)
        return clean_copy