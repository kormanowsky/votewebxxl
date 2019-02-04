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
        "votings": Voting.objects.all(),
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

# New view for a single voting
@login_required
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
        "show_form": 1
    }
    # Actions 
    if action == "save" and request.method == "POST":
        if not voting.current_user_voted(request):
            form = VoteForm(request.POST)
            answers = form.data["answers"]
            for answer in answers:
                vote = Vote(question=answer['question'], answer=answer['answer'], creator=request.user)
                vote.save()
        else:
            pass
            # TODO: Error! User cannot voting two times
        return redirect("/voting/" + str(voting.id))
    elif action == "report" and request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            item = Report(voting=voting,
                          creator=request.user, title=form.data['title'], message=form.data['message'])
            item.save()
        return JsonResponse({'is_valid': form.is_valid(), 'errors': form.errors})

    # Do we need to show the form?
    if voting.current_user_voted(request):
        context["show_form"] = 0
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
    context = {
        "html_title": "@" + request.user.username,
        "profile_owner": profile_owner,
        "votings": Voting.objects.filter(owner=profile_owner.id),
        "no_right_aside": True,
    }
    return render(request, 'profile.html', context)

@login_required
def settings(request):
    context = {
        "html_title": "Settings"
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
        form = CreateVotingForm(request.POST)
        if form.is_valid():
            formdata = form.cleaned_data
            # ...
        else:
            return JsonResponse({})
    else:
        return render(request, "voting_create.html", {
            "html_title": "Create Voting"
        })