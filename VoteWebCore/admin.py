from django.contrib import admin
from .models import *
# Model admin pages
class VotingAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'datetime_created', 'datetime_closed', 'title', 'open_stats', 'banned', 'questions')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'text', 'answers')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner')


class ActivityItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')

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