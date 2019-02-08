from datetime import datetime
from json import dumps as json_encode, loads as json_decode

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

    # Voting statuses (more statuses can be computed through summing these)
    VOTING_BANNED = 0 # User cannot view voting
    VOTING_VISIBLE = 1 # User can view voting
    VOTING_OPEN_STATS = 2 # User can view stats
    VOTING_OPEN = 4 # User can vote

    owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=300)
    banned = models.IntegerField(default=0)
    open_stats = models.BooleanField(default=True)
    datetime_closed = models.DateTimeField(null=True, blank=True)

    # Returns voting status
    def status(self, user):
        status = 0
        if not len(self.questions()):
            return status
        if not self.banned:
            status += self.VOTING_VISIBLE
        if self.open_stats or self.owner == user:
            status += self.VOTING_OPEN_STATS
        if not self.user_voted(user):
            status += self.VOTING_OPEN
        return status

    # Returns list of all voting questions
    def questions(self):
        return Question.objects.filter(voting=self.id)

    # Checks if user has voted
    def user_voted(self, user):
        if not len(self.questions()):
            return False
        for question in self.questions():
            if not question.user_voted(user):
                return False
        return True

    # Checks if current user has voted
    def current_user_voted(self, request):
        if not is_logged_in(request):
            return False
        return self.user_voted(request.user)

    # Returns human time difference between current time and voting creation time
    def creation_time_diff(self):
        return datetime_human_diff(datetime.utcnow(), self.datetime_created.replace(tzinfo=None))

    # Returns datetime_created in dd.mm.yyyy
    def datetime_created_str(self):
        return self.datetime_created.strftime("%d.%m.%Y at %H:%M")

    # Returns datetime_closed in dd.mm.yyyy
    def datetime_closed_str(self):
        if not self.datetime_closed:
            return None
        return self.datetime_closed.strftime("%d.%m.%Y")

    # Returns human time difference between current time and voting closing time
    def closed_time_diff(self):
        return datetime_human_diff(self.datetime_closed.replace(tzinfo=None), datetime.now())

    # Checks if voting is open
    def open(self):
        return not self.datetime_closed or self.datetime_closed.replace(tzinfo=None) > datetime.now()


# Question
class Question(models.Model):
    # Question types
    # Question with two buttons (usually 'yes' and 'no')
    QUESTION_BUTTONS = 0
    # Question with radio inputs
    QUESTION_SINGLE_ANSWER = 1
    # Question with checkboxes
    QUESTION_MULTIPLE_ANSWERS = 2

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, default=None, blank=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField()
    text = models.CharField(max_length=300)
    answers = JSONField(max_length=10000)

    # Returns question statistics for diagram
    def stats(self):
        stats = {}
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
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
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
    datetime_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # img = models.FileField()
    status = models.IntegerField(default=0)

    def status_str(self):
        return ["Waiting", "Declined", "Accepted"][self.status]


# Activity item
class ActivityItem(models.Model):
    # Activity item types
    # New voting
    ACTIVITY_NEW_VOTING = 0
    # Vote in voting
    ACTIVITY_VOTE = 1

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)

    # Returns human time difference between current time and voting creation time
    def creation_time_diff(self):
        return datetime_human_diff(datetime.utcnow(), self.datetime_created.replace(tzinfo=None))


# Image
class Image(models.Model):

    # Image roles
    # Avatar
    IMAGE_ROLE_AVATAR = 0

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    data = models.ImageField(upload_to=generate_file_name, null=True)
    role = models.IntegerField(default=0)

    @classmethod
    def role_str_to_int(cls, role_str):
        if role_str == "avatar":
            return cls.IMAGE_ROLE_AVATAR
        return -1

    @classmethod
    def get_avatar_url(cls, request, user=None):
        if not user:
            user = request.user
        avatar_url = "https://bizraise.pro/wp-content/uploads/2014/09/no-avatar-300x300.png"
        image = Image.objects.filter(owner=user, role=Image.IMAGE_ROLE_AVATAR).order_by('-datetime_created')
        if len(image):
            avatar_url = 'http://' + request.get_host() + image[0].data.url
        return avatar_url
