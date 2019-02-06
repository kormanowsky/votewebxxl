from django.contrib.auth.models import User
from django.db import models
from json import dumps as json_encode, loads as json_decode
from VoteWebCore.functions import *


# Special field type for JSON
class JSONField(models.CharField):

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json_decode(value)

    def to_python(self, value):
        if isinstance(value, list) or value is None:
            return value

        return json_decode(value)

    def get_prep_value(self, value):
        return json_encode(value)


# Voting
class Voting(models.Model):

    # Voting statuses
    # Public voting (visible to logged in users)
    VOTING_PUBLIC = 0
    # Banned voting (banned by admins because of reports)
    VOTING_BANNED = 1

    # Voting stats statuses
    # Closed stats
    VOTING_STATS_CLOSED = False
    # Open stats
    VOTING_STATS_OPEN = True

    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=300)
    status = models.IntegerField(default=0)
    open_stats = models.BooleanField(default=True)
    datetime_closed = models.DateTimeField(null=True, blank=True)

    # Returns list of all voting questions
    def questions(self):
        return Question.objects.filter(voting=self.id)

    # Checks if user has voted
    def user_voted(self, user):
        return self.questions()[0].user_voted(user)

    # Checks if current user has voted
    def current_user_voted(self, request):
        if not is_logged_in(request):
            return False
        return self.user_voted(request.user)

    # Returns human time difference between current time and voting creation time
    def creation_time_diff(self):
        return datetime_human_diff(datetime.utcnow(), self.datetime_created.replace(tzinfo=None))


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

    # Checks if user has voted
    def user_voted(self, user):
        return len(Vote.objects.filter(question=self.id, creator=user.id)) > 0

    # Checks if current user has voted
    def current_user_voted(self, request):
        if not is_logged_in(request):
            return False
        return self.user_voted(request.user)


# Vote
class Vote(models.Model):
    creator = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)


# Report
class Report(models.Model):

    # Report statuses
    # Report that is waiting for resolution
    REPORT_WAITING = 0
    # Report that was declined by admins
    REPORT_DECLINED = 1
    # Report that was accepted by admins
    REPORT_ACCEPTED = 2

    creator = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=256)
    message = models.CharField(max_length=512)
    # img = models.FileField()
    status = models.IntegerField(default=0)

# Activity of user
def get_activity(user, max_items=5):
    max_items = int(max_items)
    votings = Voting.objects.filter(owner=user).order_by('-datetime_created')[:max_items]
    activity_items = []
    for voting in votings:
        if voting.datetime_created:
            activity_items.append({
                "type": "new-voting",
                "voting": voting,
            })
    return activity_items