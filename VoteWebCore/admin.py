from django.contrib import admin
from .models import *
# Model admin pages
class VotingAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'questions', 'datetime_created_str', 'datetime_closed_str', 'banned', 'open', 'open_stats', )


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'voting', 'text', 'type', 'answers')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created', 'question', 'answer')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created', 'voting', 'title', 'message', 'status')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'datetime_created', 'voting', 'message')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'datetime_created', 'role', 'img')


class ActivityItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'datetime_created', 'voting', 'type')

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