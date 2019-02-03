from django.contrib.auth.models import User
from django.db import models
from json import dumps as json_encode, loads as json_decode
from VoteWebCore.functions import is_logged_in

# Special field type for JSON
class JSONField(models.CharField):

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json_decode(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value

        if value is None:
            return value

        return json_decode(value)

    def get_prep_value(self, value):
        return json_encode(value)

# Voting
class Voting(models.Model):

    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=300)

    # Returns list of all voting questions
    def questions(self):
        return Question.objects.filter(voting=self.id)


# Question
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
    answers = JSONField(max_length=10000)

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

# Vote
class Vote(models.Model):

    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)