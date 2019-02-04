from django import forms
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class SettingsForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    username = forms.CharField(max_length=32)


class VoteForm(forms.Form):

    def __init__(self, rawData, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        print(rawData)

    def parsed_answers(self):
        answers = {}
        for key in self.data.keys():
            if key.find("answers") == 0:
                question_id = int(key.split("[")[1].split("]")[0])
                answer = self.data[key]
                answers[question_id] = answer
        return answers
