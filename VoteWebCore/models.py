from django.contrib.auth.models import User
from django.db import models
from json import dumps as json_encode, load as json_decode
from VoteWebCore.functions import is_logged_in


class Voting(models.Model):

    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=300)

    # Returns list of all voting questions
    def questions(self):
        return Question.objects.filter(voting=self.id)


class Question(models.Model):

    # Question types
    # Question with two buttons (usually 'yes' and 'no')
    QUESTION_BUTTONS = 0
    # Question with radio inputs
    QUESTION_SINGLE_ANSWER = 1
    # Question with checkboxes
    QUESTION_MULTIPLE_ANSWERS = 2

    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)
    type = models.IntegerField()
    text = models.CharField(max_length=300)
    answers = models.CharField(max_length=10000)

    # In __init__() we decode answers
    def __init__(self, *args, **kwargs):
        super(models.Model, self).__init__(self, *args, **kwargs)
        self.answers = json_decode(self.answers)

    # In save() we encode answers
    def save(self, *args, **kwargs):
        self.answers = json_encode(self.answers)
        super(models.Model, self).save(*args, **kwargs)

    # Returns question statistics for diagram
    def stats(self):
        stats = {
            "all": len(Vote.objects.filter(question=self.id)),
        }
        for answer in self.answers:
            stats[answer] = len(Vote.objects.filter(question=self.id, answer=answer))
        return stats

    # Checks if current user has voted
    def current_user_voted(self, request):
        if not is_logged_in(request):
            return False
        return len(Vote.objects.filter(question=self.id, creator=request.user.id)) == 1


class Vote(models.Model):

    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)