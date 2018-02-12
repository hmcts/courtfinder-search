from django import forms
from search.models import CourtAddress, AddressType, Town, Contact
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserAddForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name= forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)

    class Meta:
        model = User
        fields = ('username', 'is_superuser', 'first_name', 'last_name', 'email')
        labels = {'is_superuser': 'Super admin'}


class CourtBasicForm(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    alert = forms.CharField(label='Urgent notice', max_length=250, required=False,
                            widget=forms.Textarea(attrs={'rows': 3}))
    info = forms.CharField(label='Additional information', max_length=4000, required=False,
                            widget=forms.Textarea(attrs={'rows': 6, 'class': 'rich-editor'}))
    displayed = forms.BooleanField(label='Open', required=False)


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
