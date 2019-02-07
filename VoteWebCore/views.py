from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from VoteWebCore.forms import *
from VoteWebCore.models import *
from VoteWebCore.functions import *

@login_required
def votings(request):
    context = {
        "votings": Voting.objects.exclude(banned=1),
        "html_title": "Voting Library",
        "no_right_aside": True
    }
    return render(request, 'voting_library.html', context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('/login')


def register(request):
    context = {
        'form': RegisterForm(request.POST)
    }
    if request.method == "POST":
        if context['form'].is_valid():
            context['form'].save()
            return redirect('/login?register_success=1')
        else:
            context['errors'] = form_errors(context['form'])
    return render(request, 'registration/registration.html', context)


def voting_save(request):
    form = SaveVotingForm(request.POST)
    if form.is_valid():
        formdata = form.data
        if not formdata['voting_id']:
            voting = Voting(owner=request.user,
                            title=formdata['title'],
                            datetime_closed=formdata['datetime_closed'],
                            open_stats=formdata['open_stats'])
            voting.save()
            activity_item = ActivityItem(user=request.user, voting=voting, type=ActivityItem.ACTIVITY_NEW_VOTING)
            activity_item.save()
        else:
            voting = Voting.objects.filter(id=formdata['voting_id'])
            if not len(voting) or not voting[0].owner == request.user:
                return JsonResponse({
                    "ErrorCode": 403,
                    "Error": "NotAllowedError"
                })
            voting.update(datetime_closed=formdata['datetime_closed'],
                          title=formdata['title'],
                          open_stats=formdata['open_stats'])
            voting = voting[0]
            voting.questions().update(voting=None)
        for question_id in formdata['questions']:
            Question.objects.filter(id=question_id).update(voting=voting)
        return redirect("/voting/" + str(voting.id))
    else:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "InvalidInputData"
        })

# New view for a single voting
def voting_single(request, voting_id=-1, action="index"):
    voting_items = Voting.objects.filter(id=voting_id)
    is_found = len(voting_items) == 1
    if not is_found:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "VoteNotFound"
        })
    voting = voting_items[0]
    context = {
        "voting": voting,
        'html_title': voting.title,
    }
    # Actions 
    if action == "save" and request.method == "POST":
        if not voting.current_user_voted(request):
            form = VoteForm(request.POST)
            answers = form.data["answers"]
            for answer in answers:
                vote = Vote(question=answer['question'], answer=answer['answer'], creator=request.user)
                vote.save()
            activity_item = ActivityItem(user=request.user, voting=voting, type=ActivityItem.ACTIVITY_VOTE)
            activity_item.save()
        else:
            return JsonResponse({
                "ErrorCode": 403,
                "Error": "NotAllowedError"
            })
        return redirect("/voting/" + str(voting.id))
    elif action == "report" and request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            item = Report(status=Report.REPORT_WAITING, voting=voting,
                          creator=request.user, title=form.data['title'], message=form.data['message'])
            item.save()
        return JsonResponse({'is_valid': form.is_valid(), 'errors': form.errors})
    elif action == "remove":
        if voting.owner == request.user:
            voting.delete()
            return redirect('/votings')
        else:
            return JsonResponse({"ErrorCode": 403, "Error": "NotAllowedError"})
    elif action == "edit":
        if voting.owner == request.user:
            if request.method == "POST":
                return voting_save(request)
            else:
                return render(request, "voting_edit.html", {
                    "html_title": "Edit | " + voting.title,
                    "voting": voting
                })
        else:
            return JsonResponse({"ErrorCode": 403, "Error": "NotAllowedError"})
    return render(request, "voting_single.html", context)


def profile(request, username=None):
    if username is None:
        if request.user.username:
            return redirect("/profile/" + request.user.username)
        else:
            return JsonResponse({
                "ErrorCode": 404,
                "Error": "UserNotFound"
            })
    profile_owner = User.objects.filter(username=username)
    if len(profile_owner) == 1:
        profile_owner = profile_owner[0]
    else:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "UserNotFound"
        })
    if profile_owner == request.user:
        reports = Report.objects.filter(creator=profile_owner)
    else:
        reports = None
    activity = ActivityItem.objects.filter(user=profile_owner.id).exclude(voting__banned=1).order_by('-datetime_created')
    votings = Voting.objects.filter(owner=profile_owner.id).exclude(banned=1).order_by("-datetime_created")
    activity_small = activity[:5]
    votings_small = votings[:5]
    context = {
        "html_title": "@" + request.user.username,
        "profile_owner": profile_owner,
        "profile_owner_reports": reports,
        "votings": votings,
        "votings_small": votings_small,
        "activity": activity,
        "activity_small": activity_small,
        "no_right_aside": True,
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
                    form.add_error('username', 'User name already register')
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


@login_required
def voting_create(request):
    if request.method == "POST":
        return voting_save(request)
    else:
        return render(request, "voting_create.html", {
            "html_title": "Create Voting", 
        })

@login_required
def remove_account(request):
    request.user.delete()
    return render(request, "registration/remove_account.html", {
        "html_title": "Remove Account"
    })

def test_upload(request):
    return render(request, "load-img-form.html", {
        "form": LoadImgForm()
    })