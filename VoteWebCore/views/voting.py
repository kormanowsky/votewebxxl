from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string

from .error import *
from .api import save_voting
from VoteWebCore.forms import VoteForm, ReportForm, CommentForm
from VoteWebCore.models import Vote, Voting, ActivityItem, Report, Comment


# Voting views


def get_voting(request, voting_id=0):
    voting_items = Voting.objects.filter(id=voting_id).exclude(is_active=False)
    if not len(voting_items):
        return error_not_found(request)
    return voting_items[0]


def index(request, voting_id=0):
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
    return render(request, "voting_single.html", {
        "voting": voting,
        'html_title': voting,
    })


def save_votes(request, voting_id=0):
    if request.method != "POST":
        return error_method_not_allowed(request)
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
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
    return redirect("/voting/{}".format(str(voting.id)))


def report(request, voting_id=0):
    if request.method != "POST":
        return error_method_not_allowed(request)
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
    form = ReportForm(request.POST)
    if form.is_valid():
        item = Report(status=Report.REPORT_WAITING, voting=voting,
                      user=request.user, title=form.data['title'], message=form.data['message'])
        item.save()
        return JsonResponse({"is_valid": True})
    return error_bad_request(request)


def remove(request, voting_id=0):
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
    if voting.user == request.user:
        voting.is_active = False
        voting.save()
        return redirect('/votings')
    else:
        return error_forbidden(request)


def edit(request, voting_id=0):
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
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


def comment(request, voting_id=0):
    if request.method != "POST":
        return error_method_not_allowed(request)
    voting = get_voting(request, voting_id)
    if not isinstance(voting, Voting):
        return voting
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


def create(request):
    if request.method == "POST":
        return save_voting(request)
    else:
        return render(request, "voting_create.html", {
            "html_title": "Create Voting",
        })