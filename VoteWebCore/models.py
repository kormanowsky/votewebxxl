from datetime import datetime
from json import dumps as json_encode, loads as json_decode

from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe

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
    # User cannot view voting
    VOTING_BANNED = 0
    # User can view voting
    VOTING_VISIBLE = 1
    # User can view stats
    VOTING_OPEN_STATS = 2
    # User can vote
    VOTING_OPEN = 4

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    title = models.CharField(max_length=300)
    banned = models.BooleanField(default=False)
    open_stats = models.BooleanField(default=True)
    datetime_closed = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Returns voting status
    def status(self, user):
        status = self.VOTING_BANNED
        if not len(self.questions()) or self.banned:
            return status
        else:
            status += self.VOTING_VISIBLE
        if self.open_stats or self.user == user:
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
        if not request.user.is_authenticated:
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
        return len(ActivityItem.objects.filter(type=ActivityItem.ACTIVITY_FAVOURITE, voting=self.id, user=user.id).exclude(is_active=False))

    # Checks if current user added to favourites
    def current_user_added_to_favourites(self, request):
        return self.user_added_to_favourites(request.user)

    # Returns count of favourites
    def favourites_count(self):
        return len(ActivityItem.objects.filter(type=ActivityItem.ACTIVITY_FAVOURITE, voting=self.id).exclude(is_active=False))
    favourites_count.short_description = "Count of additions to Favourites"

    # Returns comments list
    def comments(self):
        return Comment.objects.filter(voting=self.id).order_by("-datetime_created").exclude(is_active=False)

    # Returns comments count
    def comments_count(self):
        return len(self.comments())
    comments_count.short_description = "Comments count"

    # HTML for questions field in admin panel
    def questions_html(self):
        return questions_html(self.questions())
    questions_html.short_description = "Questions"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self.user)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "{} (#{})".format(self.title, self.id)


# Question
class Question(models.Model):

    # Question types

    # Question with two buttons (usually 'yes' and 'no')
    QUESTION_BUTTONS = 0
    # Question with radio inputs
    QUESTION_SINGLE_ANSWER = 1
    # Question with checkboxes
    QUESTION_MULTIPLE_ANSWERS = 2

    QUESTION_TYPES = [
        (QUESTION_BUTTONS, 'Buttons'),
        (QUESTION_SINGLE_ANSWER, 'Radio inputs'),
        (QUESTION_MULTIPLE_ANSWERS, 'Checkboxes')
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, default=None, blank=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField(choices=QUESTION_TYPES)
    text = models.CharField(max_length=300)
    answers = JSONField(max_length=10000)
    is_active = models.BooleanField(default=True)

    # Returns question statistics for diagram
    def stats(self):
        stats = {}
        for answer in self.answers:
            stats[answer] = len(Vote.objects.filter(question=self.id, answer=answer).exclude(is_active=False))
        return stats

    # Checks if user has voted
    def user_voted(self, user):
        return len(Vote.objects.filter(question=self.id, user=user.id)) > 0

    # Checks if current user has voted
    def current_user_voted(self, request):
        if not request.user.is_authenticated:
            return False
        return self.user_voted(request.user)

    # HTML for voting field in admin panel
    def voting_html(self):
        return voting_html(self)
    voting_html.short_description = "Voting"

    # HTML for answers field in admin panel
    def answers_html(self):
        return mark_safe("<br/>".join(list(map(str, self.answers))))
    answers_html.short_description = "Answers"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "{} (#{})".format(self.text, self.id)


# Vote
class Vote(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    # Returns datetime_created in dd.mm.yyyy
    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # HTML for question field in admin panel
    def question_html(self):
        return question_html(self.question)
    question_html.short_description = "Question"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self.user)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "Vote #{}".format(self.id)


# Report
class Report(models.Model):

    # Report statuses

    # Report that is waiting for resolution
    REPORT_WAITING = 0
    # Report that was declined by admins
    REPORT_DECLINED = 1
    # Report that was accepted by admins
    REPORT_ACCEPTED = 2

    REPORT_STATUSES = [
        (REPORT_WAITING, 'Waiting'),
        (REPORT_DECLINED, 'Declined'),
        (REPORT_ACCEPTED, 'Accepted')
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=256)
    message = models.CharField(max_length=512)
    datetime_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.IntegerField(default=REPORT_WAITING, choices=REPORT_STATUSES)
    is_active = models.BooleanField(default=True)

    # Returns datetime_created as a readable string
    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # HTML for voting field in admin panel
    def voting_html(self):
        return voting_html(self)
    voting_html.short_description = "Voting"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "Report #{}".format(self.id)


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

    ACTIVITY_TYPES = [
        (ACTIVITY_NEW_VOTING, 'New voting'),
        (ACTIVITY_VOTE, 'Vote'),
        (ACTIVITY_FAVOURITE, 'Added to favourite'),
        (ACTIVITY_COMMENT, 'Comment'),
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    type = models.IntegerField(default=ACTIVITY_NEW_VOTING, choices=ACTIVITY_TYPES)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    # Returns data for activity_item.html
    def display_data(self):
        text = ["created voting", "voted in", "added to favourites"][self.type]
        icon = ["question", "check-square", "star"][self.type]
        return {
            "text": text, 
            "icon": icon
        }

    # Returns human time difference between current time and voting creation time
    def creation_time_diff(self):
        return datetime_human_diff(datetime.utcnow(), self.datetime_created.replace(tzinfo=None))

    # Returns datetime_created as a readable string
    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # HTML for voting field in admin panel
    def voting_html(self):
        return voting_html(self.voting)
    voting_html.short_description = "Voting"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self.user)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "Activity item #{}".format(self.id)


# Image
class Image(models.Model):

    # Image roles

    # Avatar
    IMAGE_ROLE_AVATAR = 0

    IMAGE_ROLES = [
        (IMAGE_ROLE_AVATAR, 'Avatar')
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)
    data = models.ImageField(upload_to=generate_file_name, null=True)
    role = models.IntegerField(default=IMAGE_ROLE_AVATAR, choices=IMAGE_ROLES)
    is_active = models.BooleanField(default=True)

    # Returns datetime_created as a readable string
    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self)
    user_html.short_description = "User"

    # Image data for admin panel
    def img(self):
        return format_html('<img height=100 src="{0}">',
                           mark_safe(self.data.url)
                           )
    img.short_description = 'Image'

    # Convert to string (for site admin panel)
    def __str__(self):
        return "Image #{}".format(self.id)

    # Converts string role to int role
    @classmethod
    def role_str_to_int(cls, role_str):
        for role in roles:
            if role[1].lower() == role_str.replace("_", " "):
                return role[0]
        return -1

    # Returns avatar url for specified user
    @classmethod
    def get_avatar_url(cls, request, user=None):
        if not user:
            user = request.user
        avatar_url = "https://bizraise.pro/wp-content/uploads/2014/09/no-avatar-300x300.png"
        image = Image.objects.filter(user=user, role=Image.IMAGE_ROLE_AVATAR).order_by('-datetime_created')
        if len(image):
            avatar_url = 'http://' + request.get_host() + image[0].data.url
        return avatar_url


# Comment
class Comment(models.Model):

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)
    voting = models.ForeignKey(to=Voting, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=512)
    datetime_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Returns datetime_created as a readable string
    def datetime_created_str(self):
        return datetime_human(self.datetime_created)
    datetime_created_str.short_description = "Datetime of creation"

    # HTML for voting field in admin panel
    def voting_html(self):
        return voting_html(self)
    voting_html.short_description = "Voting"

    # HTML for user field in admin panel
    def user_html(self):
        return user_html(self)
    user_html.short_description = "User"

    # Convert to string (for site admin panel)
    def __str__(self):
        return "Comment #{}".format(self.id)