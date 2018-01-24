from django import forms


class CourtBasicForm(forms.Form):
    name = forms.CharField(label='Name', max_length=200)
    alert = forms.CharField(label='Urgent notice', max_length=250, required=False,
                            widget=forms.Textarea(attrs={'rows': 3}))
    info = forms.CharField(label='Additional information', max_length=4000, required=False,
                            widget=forms.Textarea(attrs={'rows': 6}))
    displayed = forms.BooleanField(label='Open', required=False)
