from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .error import *
from VoteWebCore.forms import VoteForm, ReportForm, CommentForm, SaveVotingForm
from VoteWebCore.models import Vote, Voting, ActivityItem, Report, Comment, Question


# Voting views


def get_voting(voting_id):
    voting_items = Voting.objects.filter(id=voting_id).exclude(is_active=False)
    if not len(voting_items):
        return None
    return voting_items[0]


def index(request, voting):
    after = request.GET.get('after', '')
    if len(after):
        message = ""
        if voting.user == request.user:
            if after == "edit":
                message = "Voting was updated."
            elif after == "create":
                message = "Voting was created."
        elif after == "remove_comment":
            comment_id = int(request.GET.get('comment_id', 0))
            comment = Comment.objects.filter(id=comment_id)
            if len(comment) and comment[0].user == request.user:
                message = "Comment was removed."
        elif after == "vote":
            message = "Your votes were saved."
        if len(message):
            messages.add_message(request, messages.SUCCESS, message)
    return render(request, "voting_single.html", {
        "voting": voting,
        'html_title': voting,
    })


@login_required
def save_voting(request):
    if request.method != 'POST':
        return error_method_not_allowed(request)
    form = SaveVotingForm(request.POST)
    if form.is_valid():
        formdata = form.data
        if not formdata['voting_id']:
            voting = Voting(user=request.user,
                            title=formdata['title'],
                            datetime_closed=formdata['datetime_closed'],
                            open_stats=formdata['open_stats'])
            voting.save()
            activity_item = ActivityItem(user=request.user, voting=voting, type=ActivityItem.ACTIVITY_NEW_VOTING)
            activity_item.save()
            after_action = "create"
        else:
            voting = Voting.objects.exclude(is_active=False).get(id=formdata['voting_id'])
            if voting.user != request.user:
                return error_forbidden(request)
            voting.datetime_closed = formdata['datetime_closed']
            voting.title = formdata['title']
            voting.open_stats = formdata['open_stats']
            voting.save()
            after_action = "edit"
        # If questions of voting were changed (e.g a question was added or removed),
        # we remove all votes of this voting
        question_ids = []
        for question in voting.questions():
            question_ids.append(question.id)
        if question_ids != formdata['questions']:
            for question_id in question_ids:
                Vote.objects.filter(question=question_id).update(is_active=False)
        # Now we "remove" all questions of voting, then we will recover them
        voting.questions().update(is_active=False, voting=None)
        # Here we add voting to new questions
        for question_id in formdata['questions']:
            Question.objects.filter(id=question_id).update(is_active=True, voting=voting)
        return redirect("/voting/{}?after={}".format(voting.id, after_action))
    return error_bad_request(request)


@login_required
def save(request, voting):
    if request.method != "POST":
        return error_method_not_allowed(request)
    if voting.current_user_voted(request):
        return error_forbidden(request)
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
    return redirect("/voting/{}?after=vote".format(voting.id))


@login_required
def report(request, voting):
    if request.method != "POST":
        return error_method_not_allowed(request)
    form = ReportForm(request.POST)
    if form.is_valid():
        item = Report(status=Report.REPORT_WAITING, voting=voting,
                      user=request.user, title=form.data['title'], message=form.data['message'])
        item.save()
        return JsonResponse({"is_valid": True})
    return error_bad_request(request)


@login_required
def remove(request, voting):
    if voting.user == request.user:
        voting.is_active = False
        voting.save()
        return redirect('/votings?after_remove={}'.format(voting.id))
    else:
        return error_forbidden(request)


@login_required
def edit(request, voting):
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


@login_required
def comment(request, voting):
    if request.method != "POST":
        return error_method_not_allowed(request)
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


def view_voting(request, voting_id=0, action="index"):
    voting = get_voting(voting_id)
    if action in globals() and voting is not None:
        return globals()[action](request, voting)
    return error_not_found(request)


@login_required
def create_voting(request):
    if request.method == "POST":
        return save_voting(request)
    else:
        return render(request, "voting_create.html", {
            "html_title": "Create Voting",
        })
