from datetime import datetime
from json import dumps as json_encode, loads as json_decode

from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
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
    banned = models.BooleanField(default=False)
    open_stats = models.BooleanField(default=True)
    datetime_closed = models.DateTimeField(null=True, blank=True)

    # Returns voting status
    def status(self, user):
        status = self.VOTING_BANNED
        if not len(self.questions()):
            return status
        if self.banned:
            return status
        else:
            status += self.VOTING_VISIBLE
        if self.open_stats or self.owner == user:
            status += self.VOTING_OPEN_STATS
        if self.open() and not self.user_voted(user):
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
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # Returns datetime_closed in dd.mm.yyyy
    def datetime_closed_str(self):
        if not self.datetime_closed:
            return None
        return date_human(self.datetime_closed)
    datetime_closed_str.short_description = "Date of closing"

    # Returns human time difference between current time and voting closing time
    def closed_time_diff(self):
        return datetime_human_diff(self.datetime_closed.replace(tzinfo=None), datetime.now())

    # Checks if voting is open
    def open(self):
        return not self.datetime_closed or self.datetime_closed.replace(tzinfo=None) > datetime.now()
    open.boolean = True
    # Checks if user added to favourites
    def user_added_to_favourites(self, user):
        return len(ActivityItem.objects.filter(type=ActivityItem.ACTIVITY_FAVOURITE, voting=self.id, user=user.id))

    # Checks if current user added to favourites
    def current_user_added_to_favourites(self, request):
        return self.user_added_to_favourites(request.user)\

    # Returns count of favourites
    def favourites_count(self):
        return len(ActivityItem.objects.filter(type=ActivityItem.ACTIVITY_FAVOURITE, voting=self.id))
    favourites_count.short_description = "Count of additions to Favourites"
    # Returns comments
    def comments(self):
        return Comment.objects.filter(voting=self.id).order_by("-datetime_created")

    def comments_count(self):
        return len(self.comments())
    comments_count.short_description = "Comments count"

    def questions_html(self):
        if not len(self.questions()):
            return "-"
        html = ""
        for question in self.questions():
            html += '<a href="/admin/VoteWebCore/question/%d/change">%s (#%s)</a><br/>' % (question.id, question.text, str(question.id))
        return mark_safe(html)
    questions_html.short_description = "Questions"

    def owner_html(self):
        if not self.owner:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.owner.id, self.owner.first_name, self.owner.last_name, self.owner.username))
    owner_html.short_description = "Owner"

    def __str__(self):
        return self.title + " (#" + str(self.id) + ")"


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
    type = models.IntegerField(choices=(
        (QUESTION_BUTTONS, 'Buttons'),
        (QUESTION_SINGLE_ANSWER, 'Radio inputs'),
        (QUESTION_MULTIPLE_ANSWERS, 'Checkboxes')
    ))
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

    def __str__(self):
        return self.text + " (#" + str(self.id) + ")"

    def voting_html(self):
        if not self.voting:
            return "-"
        return mark_safe('<a href="/admin/VoteWebCore/voting/%d/change">%s (#%d)</a><br/>'
                         % (self.voting.id, self.voting.title, self.voting.id))
    voting_html.short_description = "Voting"

    def answers_html(self):
        return mark_safe("<br/>".join(list(map(str, self.answers))))
    answers_html.short_description = "Answers"

    def owner_html(self):
        if not self.owner:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.owner.id, self.owner.first_name, self.owner.last_name, self.owner.username))
    owner_html.short_description = "Owner"


# Vote
class Vote(models.Model):
    creator = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)

    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    def question_html(self):
        question = self.question
        html = '<a href="/admin/VoteWebCore/question/%d/change">%s (#%s)</a><br/>' % (
        question.id, question.text, str(question.id))
        return mark_safe(html)
    question_html.short_description = "Question"

    def creator_html(self):
        if not self.creator:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.creator.id, self.creator.first_name, self.creator.last_name, self.creator.username))
    creator_html.short_description = "Creator"




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
    status = models.IntegerField(default=0, choices=(
        (REPORT_WAITING, 'Waiting'),
        (REPORT_DECLINED, 'Declined'),
        (REPORT_ACCEPTED, 'Accepted')
    ))

    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    def voting_html(self):
        if not self.voting:
            return "-"
        return mark_safe('<a href="/admin/VoteWebCore/voting/%d/change">%s (#%d)</a><br/>'
                         % (self.voting.id, self.voting.title, self.voting.id))
    voting_html.short_description = "Voting"

    def creator_html(self):
        if not self.creator:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.creator.id, self.creator.first_name, self.creator.last_name, self.creator.username))
    creator_html.short_description = "Creator"


# Activity item
class ActivityItem(models.Model):
    # Activity item types
    # New voting
    ACTIVITY_NEW_VOTING = 0
    # Vote in voting
    ACTIVITY_VOTE = 1
    # Add to favourites
    ACTIVITY_FAVOURITE = 2
    # Comment on voting
    ACTIVITY_COMMENT = 3

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    type = models.IntegerField(default=0, choices=(
        (ACTIVITY_NEW_VOTING, 'New voting'),
        (ACTIVITY_VOTE, 'Vote'),
        (ACTIVITY_FAVOURITE, 'Added to favourite'),
        (ACTIVITY_COMMENT, 'Comment'),
    ))
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)

    # Returns human time difference between current time and voting creation time
    def creation_time_diff(self):
        return datetime_human_diff(datetime.utcnow(), self.datetime_created.replace(tzinfo=None))
    
    def display_data(self):
        text = ["created voting", "voted in", "added to favourites", "added comment to"][self.type]
        icon = ["question", "check-square", "star", "comment"][self.type]
        return {
            "text": text, 
            "icon": icon
        }

    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    def voting_html(self):
        if not self.voting:
            return "-"
        return mark_safe('<a href="/admin/VoteWebCore/voting/%d/change">%s (#%d)</a><br/>'
                         % (self.voting.id, self.voting.title, self.voting.id))
    voting_html.short_description = "Voting"

    def user_html(self):
        if not self.user:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.user.id, self.user.first_name, self.user.last_name, self.user.username))
    user_html.short_description = "User"



# Image
class Image(models.Model):

    # Image roles
    # Avatar
    IMAGE_ROLE_AVATAR = 0

    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    data = models.ImageField(upload_to=generate_file_name, null=True)
    role = models.IntegerField(default=0, choices=[(IMAGE_ROLE_AVATAR, 'Avatar')])

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

    # Admin panel
    def img(self):
        src = self.data.url
        return mark_safe('<img height=100 src="%s">' % src)
    img.short_description = 'Image'

    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    def owner_html(self):
        if not self.owner:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.owner.id, self.owner.first_name, self.owner.last_name, self.owner.username))
    owner_html.short_description = "Owner"


# Comment
class Comment(models.Model):

    creator = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=512)
    datetime_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    def voting_html(self):
        if not self.voting:
            return "-"
        return mark_safe('<a href="/admin/VoteWebCore/voting/%d/change">%s (#%d)</a><br/>'
                         % (self.voting.id, self.voting.title, self.voting.id))
    voting_html.short_description = "Voting"

    def creator_html(self):
        if not self.creator:
            return "-"
        return mark_safe('<a href="/admin/auth/user/%d/change/">%s %s</a><br/>@%s' % (self.creator.id, self.creator.first_name, self.creator.last_name, self.creator.username))
    creator_html.short_description = "Creator"
