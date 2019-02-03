from django import forms


class ChangeUserData(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    user_name = forms.CharField(max_length=32)
