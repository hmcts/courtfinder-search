from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UsernameField
from search.models import Court, CourtAddress, AddressType, Town, Contact


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


class CourtBasicForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ('name', 'alert', 'info', 'displayed')
        labels = {'alert': 'Urgent notice', 'displayed': 'Open', 'info': 'Additional information'}
        widgets = {
            'alert': forms.Textarea(attrs={'rows': 3}),
            'info': forms.Textarea(attrs={'rows': 6, 'class': 'rich-editor'})
        }


class CourtLocationForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ('directions', 'lat', 'lon')
        labels = {'directions': 'Local Information', 'lat': 'Latitude', 'lon': 'Longitude'}
        widgets = {'directions': forms.Textarea(attrs={'rows': 4}),}


class LocatePostcodeForm(forms.Form):
    postcode = forms.CharField(max_length=9)


class CourtAddressForm(forms.ModelForm):
    class Meta:
        model = CourtAddress
        fields = ['address_type', 'address', 'town', 'postcode']

    def __init__(self, address_index=None, court=None, *args, **kwargs):
        super(CourtAddressForm, self).__init__(*args, **kwargs)
        address_types = AddressType.objects.all()
        self.fields['town'].queryset = Town.objects.all().order_by('name')
        if address_index and address_index > 0:
            address_types = address_types.exclude(name="Visit us or write to us")
            if court:
                primary_address_type = court.primary_address().address_type
                if not primary_address_type.name == "Visit us or write to us":
                    address_types = address_types.exclude(name=primary_address_type.name)
                else:
                    address_types = AddressType.objects.none()
        if hasattr(self.instance, 'address_type'):
            if self.instance.address_type not in address_types:
                self.fields["address"].disabled = True
                self.fields["postcode"].disabled = True
                self.fields["town"].disabled = True
        self.fields['address_type'].queryset = address_types


class CourtContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'number', 'explanation', 'in_leaflet', 'sort_order']

    def __init__(self, *args, **kwargs):
        super(CourtContactForm, self).__init__(*args, **kwargs)
        self.fields["explanation"].required = False
        self.fields['sort_order'].widget = forms.HiddenInput()
        self.fields['sort_order'].required = False
