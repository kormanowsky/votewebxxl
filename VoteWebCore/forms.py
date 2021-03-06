from querystring_parser import parser as qs_parser
from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm

from VoteWebCore.models import *
from VoteSimple.settings import CSRF_KEY


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
        raw_answers = qs_parser.parse(raw_data.urlencode(), normalized=True)
        del raw_answers[CSRF_KEY]
        answers = []
        for answer_key in raw_answers:
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


class SaveVotingForm(forms.Form):
    title = forms.CharField(max_length=300)
    questions = list()
    voting_id = forms.IntegerField()
    datetime_closed = forms.DateField()
    open_stats = forms.BooleanField()

    def __init__(self, raw_data, *args, **kwargs):
        super(SaveVotingForm, self).__init__(*args, **kwargs)
        parsed_data = qs_parser.parse(raw_data.urlencode(), normalized=True)
        del parsed_data[CSRF_KEY]
        if not isinstance(parsed_data['questions'], list):
            parsed_data['questions'] = [parsed_data['questions']]
        for i, question in enumerate(parsed_data['questions']):
            parsed_data['questions'][i] = int(question)
        parsed_data['voting_id'] = int(parsed_data['voting_id'])
        if len(parsed_data['datetime_closed_date']):
            parsed_data['datetime_closed'] = datetime_to_utc(datetime_str_to_obj("{} {}".format(parsed_data['datetime_closed_date'], parsed_data['datetime_closed_time'])))
        else:
            parsed_data['datetime_closed'] = None
        parsed_data['open_stats'] = parsed_data['open_stats'] == '1'
        self.data = parsed_data

    def is_valid(self):
        return len(self.data['questions']) > 0


class QuestionForm(forms.Form):
    question_id = forms.IntegerField()
    text = forms.CharField(max_length=100)
    type = forms.IntegerField(min_value=0, max_value=2)
    answers = list()
    image_id = forms.IntegerField()

    def __init__(self, raw_data, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        parsed_data = qs_parser.parse(raw_data.urlencode(), normalized=True)
        del parsed_data[CSRF_KEY]
        parsed_data['type'] = int(parsed_data['type'])
        parsed_data['question_id'] = int(parsed_data['question_id'])
        if len(parsed_data['image_id']):
            parsed_data['image_id'] = int(parsed_data['image_id'])
        else:
            parsed_data['image_id'] = 0
        self.data = parsed_data

    def is_valid(self):
        if len(self.data['answers']) < 2:
            return False
        if not (Question.QUESTION_BUTTONS <= self.data['type'] <= Question.QUESTION_MULTIPLE_ANSWERS):
            return False
        return len(form_errors(self)) == 0


class LoadImgForm(forms.Form):
    file = forms.ImageField()



class VotingsSearchForm(forms.Form):
    title = forms.CharField(max_length=100, required=False)
    user = forms.CharField(max_length=100, required=False)
    datetime_created_from = forms.DateTimeField(required=False)
    datetime_created_to = forms.DateTimeField(required=False)

    def __init__(self, raw_data, *args, **kwargs):
        super(VotingsSearchForm, self).__init__(*args, **kwargs)
        self.data['title'] = raw_data.get('title', '')
        self.data['user'] = raw_data.get('user', '')
        datetime_from_obj = datetime_str_to_obj(raw_data.get("datetime_created_from", ''))
        if datetime_from_obj is not None:
            datetime_from_obj = datetime_to_utc(datetime_from_obj)
        self.data['datetime_created_from'] = datetime_from_obj
        datetime_to_obj = datetime_str_to_obj(raw_data.get("datetime_created_to", ''))
        if datetime_to_obj is not None:
            datetime_to_obj = datetime_to_utc(datetime_to_obj) + timedelta(days=1) - timedelta(seconds=1)
        self.data['datetime_created_to'] = datetime_to_obj

    def is_valid(self):
        return not len(self.errors.as_text())


class CommentForm(forms.Form):
    message = forms.CharField(max_length=512)
