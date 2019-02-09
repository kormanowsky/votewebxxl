from django.contrib import admin
from .models import *

# Admin panel pages


class VotingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'title', 'questions_html', 'datetime_created_str', 'datetime_closed_str', 'banned', 'open', 'open_stats', 'is_active')
    list_filter = ('datetime_created', 'datetime_closed', 'banned',
    'open_stats', 'is_active')
    search_fields = ('title', 'user__first_name', 'user__last_name', 'user__username')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'voting_html', 'text', 'type', 'answers_html', 'is_active')
    search_fields = ('text', 'user__first_name', 'user__last_name', 'user__username', 'voting__title')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'datetime_created_str', 'question_html', 'answer')
    list_filter = ['datetime_created', 'is_active']
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'datetime_created_str', 'voting_html', 'title', 'message', 'status', 'is_active')
    list_filter = ('status', 'datetime_created', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'voting__title')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'datetime_created_str', 'voting_html', 'message', 'is_active')
    list_filter = ['datetime_created', 'is_active']
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'voting__title')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'datetime_created_str', 'role', 'img', 'is_active')
    list_filter = ('datetime_created', 'role', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


class ActivityItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_html', 'datetime_created_str', 'voting', 'type', 'is_active')
    list_filter = ('datetime_created', 'type', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'voting__title')


# Registration of admin pages
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