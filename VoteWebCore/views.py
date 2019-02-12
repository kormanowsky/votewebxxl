from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, render_to_response
from django.views import View
from django.template.context_processors import csrf


from VoteWebCore.api_views import save_voting
from VoteWebCore.error_views import *
from VoteWebCore.forms import *
from VoteWebCore.functions import *
from VoteSimple.settings import LOGIN_REDIRECT_URL


def index(request):
    return render(request, "index.html", {
        "html_title": "Home"
    })


@login_required
def votings(request):
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
            for error in form_errors(context['form']):
                messages.add_message(request, messages.ERROR, error)
    return render(request, 'registration.html', context)


# New view for a single voting
def voting_single(request, voting_id=-1, action="index"):
    voting_items = Voting.objects.filter(id=voting_id).exclude(is_active=False)
    is_found = len(voting_items) == 1
    if not is_found:
        return error_not_found(request)
    voting = voting_items[0]
    context = {
        "voting": voting,
        'html_title': voting.title,
    }
    # Actions
    if action != "index" and not request.user.is_authenticated:
        return error_forbidden(request)
    if action == "save" and request.method == "POST":
        if not voting.current_user_voted(request):
            form = VoteForm(request.POST)
            answers = form.data["answers"]
            questions = []
            for answer in answers:
                questions.append(answer['question'])
            for question in voting.questions():
                if question not in questions:
                    return error_bad_request(request)
            for answer in answers:
                vote = Vote(question=answer['question'], answer=answer['answer'], user=request.user)
                vote.save()
            activity_item = ActivityItem(user=request.user, voting=voting, type=ActivityItem.ACTIVITY_VOTE)
            activity_item.save()
        else:
            return error_forbidden(request)
        return redirect("/voting/" + str(voting.id))
    elif action == "report" and request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            item = Report(status=Report.REPORT_WAITING, voting=voting,
                          user=request.user, title=form.data['title'], message=form.data['message'])
            item.save()
            return JsonResponse({"is_valid": True})
        return error_bad_request(request)
    elif action == "remove":
        if voting.user == request.user:
            voting.is_active = False
            voting.save()
            return redirect('/votings')
        else:
            return error_forbidden(request)
    elif action == "edit":
        if voting.user == request.user:
            if request.method == "POST":
                return save_voting(request)
            else:
                return render(request, "voting_edit.html", {
                    "html_title": "Edit | " + voting.title,
                    "voting": voting
                })
        else:
            return error_forbidden(request)
    elif action == "comment":
        form = CommentForm(request.POST)
        if form.is_valid():
            item = Comment(user=request.user, message=form.data['message'], voting=voting)
            item.save()
            return JsonResponse({
                "is_valid": True,
                "comments_count": len(voting.comments()),
                "comment": render_to_string(request=request, template_name="comment.html", context={
                    "comment": item
                })
            })
        return error_bad_request(request)
    return render(request, "voting_single.html", context)


def profile(request, username=None):
    if username is None:
        if request.user.is_authenticated:
            return redirect("/profile/" + request.user.username)
        else:
            return error_not_found(request)
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


@login_required
def voting_create(request):
    if request.method == "POST":
        return save_voting(request)
    else:
        return render(request, "voting_create.html", {
            "html_title": "Create Voting",
        })


@login_required
def remove_account(request):
    request.user.is_active = False
    request.user.save()
    return render(request, "remove_account.html", {
        "html_title": "Remove Account"
    })


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(LOGIN_REDIRECT_URL)
        else:
            if int(request.GET.get('register_success', '0')) == 1:
                messages.add_message(request, messages.SUCCESS,
                                     'Your registration process has finished successfully. You may now log in.')
            return render(request, 'login.html', context=csrf(request))

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid() or form.get_user() is None:
            messages.add_message(request, messages.ERROR, 'Authentication data is empty or incorrect')
        else:
            auth.login(request, form.get_user())
            next = request.GET.get('next', LOGIN_REDIRECT_URL)
            return redirect(next)
        return render(request, 'login.html', context=csrf(request))
