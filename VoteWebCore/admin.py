from django.contrib import admin
from .models import *
# Model admin pages
class VotingAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'questions_html', 'datetime_created_str', 'datetime_closed_str', 'banned', 'open', 'open_stats', )


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'voting_html', 'text', 'type', 'answers_html')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created_str', 'question_html', 'answer')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created_str', 'voting_html', 'title', 'message', 'status')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created_str', 'voting_html', 'message')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'datetime_created_str', 'role', 'img')


class ActivityItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'datetime_created_str', 'voting', 'type')

# Registration
admin.site.site_header = "VoteWebXXL | Admin Panel"
admin.site.site_title = "VoteWebXXL | Admin Panel"
admin.site.index_title = ""
for model in [
    [Voting, VotingAdmin],
    [Question, QuestionAdmin],
    [Vote, VoteAdmin],
    [Report, ReportAdmin],
    [Comment, CommentAdmin],
    [Image, ImageAdmin],
    [ActivityItem, ActivityItemAdmin]
]:
    admin.site.register(model[0], model[1])