from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.files import File

from VoteWebCore.models import *
# https://github.com/bernii/querystring-parser
from querystring_parser import parser


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
    answers = dict()

    def __init__(self, raw_data, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        raw_answers = parser.parse(raw_data.urlencode(), normalized=True)
        answers = []
        for answer_key in raw_answers:
            if answer_key != "csrfmiddlewaretoken":
                question_id = int(answer_key[answer_key.find("_") + 1:])
                question_answers = raw_answers[answer_key]
                if not isinstance(question_answers, list):
                    question_answers = [question_answers]
                for answer in question_answers:
                    answers.append({
                        "question": Question(id=question_id),
                        "answer": answer
                    })
        self.data["answers"] = answers


class ReportForm(forms.Form):
    title = forms.CharField(max_length=256)
    message = forms.CharField(max_length=512)


class CreateVotingForm(forms.Form):
    title = forms.CharField(max_length=300)
    questions = list()

    def __init__(self, raw_data, *args, **kwargs):
        super(CreateVotingForm, self).__init__(*args, **kwargs)
        parsed_data = parser.parse(raw_data.urlencode(), normalized=True)
        del parsed_data['csrfmiddlewaretoken']
        for i, question in enumerate(parsed_data['questions']):
            parsed_data['questions'][i]['type'] = int(question['type'])
        self.data = parsed_data

    def is_valid(self):
        for question in self.data['questions']:
            if not 0 <= question['type'] <= 2:
                return False
        return True


class LoadImgForm(forms.Form):
    file = forms.ImageField()

    def add_photo(self, photo_file):
        with open(photo_file) as f:
            my_file = File(f)
            filename = "filename.jpg"
            self.photo_file.save(filename, my_file)
