from django import forms


class ChangeUserDataForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    username = forms.CharField(max_length=32)
