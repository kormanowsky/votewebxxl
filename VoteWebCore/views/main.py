from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from VoteWebCore.views.error import *
from VoteWebCore.forms import *
from VoteWebCore.functions import *


# Main pages' views


def index(request):
    return render(request, "index.html", {
        "html_title": "Home"
    })


def votings(request):
    after_remove = int(request.GET.get('after_remove', 0))
    voting = Voting.objects.filter(id=after_remove)
    if len(voting) and voting[0].user == request.user and voting[0].is_active == False:
        messages.add_message(request, messages.SUCCESS, 'Voting was removed.')

    votings_items = Voting.objects.exclude(is_active=False)
    form = VotingsSearchForm(request.GET)
    if form.is_valid():
        votings_items = votings_items.filter(title__contains=form.data['title'])
        votings_items = votings_items.filter(
            Q(user__last_name__contains=form.data['user']) |
            Q(user__first_name__contains=form.data['user']) |
            Q(user__username__contains=form.data['user']))
        if not form.data['datetime_created_from'] is None:
            votings_items = votings_items.filter(datetime_created__gte=form.data['datetime_created_from'])
        if not form.data['datetime_created_to'] is None:
            votings_items = votings_items.filter(datetime_created__lte=form.data['datetime_created_to'])
        votings_items = votings_items.exclude(banned=1)
    context = {
        "votings": votings_items,
        "html_title": "Votings",
        "form": form,
        "no_right_aside": True
    }
    return render(request, 'votings.html', context)


def profile(request, username=None):
    after = request.GET.get('after')
    if after == "remove_report":
        report_id = int(request.GET.get('report_id', 0))
        report = Report.objects.filter(id=report_id)
        if len(report) and report[0].user == request.user and report[0].is_active == False:
            messages.add_message(request, messages.SUCCESS, 'Report was deleted.')

    profile_user = User.objects.filter(username=username).exclude(is_active=False)
    if len(profile_user) == 1:
        profile_user = profile_user[0]
    else:
        return error_not_found(request)
    if profile_user == request.user:
        reports = Report.objects.filter(user=profile_user) \
            .order_by("-datetime_created").exclude(is_active=False)
    else:
        reports = None
    activity = ActivityItem.objects.filter(user=profile_user.id) \
        .exclude(voting__banned=1).order_by('-datetime_created').exclude(is_active=False)
    votings = Voting.objects.filter(user=profile_user.id) \
        .exclude(banned=1).order_by("-datetime_created").exclude(is_active=False)
    activity_small = activity[:5]
    votings_small = votings[:5]
    votes_count = len(activity.filter(type=ActivityItem.ACTIVITY_VOTE))
    favourite_votings = []
    favourite = activity.filter(type=ActivityItem.ACTIVITY_FAVOURITE)
    for item in favourite:
        favourite_votings.append(item.voting)
    context = {
        "html_title": "@" + request.user.username,
        "profile_user": profile_user,
        "profile_user_reports": reports,
        "votings": votings,
        "votings_small": votings_small,
        "activity": activity,
        "activity_small": activity_small,
        "favourite_votings": favourite_votings,
        "votes_count": votes_count,
        "no_right_aside": True
    }
    return render(request, 'profile.html', context)


@login_required
def settings(request):
    context = {
        "html_title": "Settings",
    }
    if request.method == "POST":
        form = SettingsForm(request.POST)
        context['form'] = form
        if form.is_valid():
            formdata = form.cleaned_data
            if request.user.username != formdata['username']:
                if len(User.objects.filter(username=formdata['username'])):
                    messages.add_message(request, messages.ERROR, "Username is already in use")
                    return render(request, 'settings.html', context)
            item = User.objects.filter(id=request.user.id)
            if len(item):
                item = item[0]
                item.username = formdata['username']
                item.first_name = formdata['first_name']
                item.last_name = formdata['last_name']
                item.email = formdata['email']
                item.save()
                request.user = item
    return render(request, "settings.html", context)
