from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect

from VoteWebCore.models import *
from VoteWebCore.forms import *
from VoteWebCore.error_views import *

# Get one question
def get_question(request, id=0):
    question = Question.objects.filter(id=id)
    if not len(question):
        return error_not_found(request)
    question = question[0]

    if question.voting is not None:
        voting_id = question.voting.id
    else:
        voting_id = None
    if question.user is not None:
        user_id = question.user.id
    else:
        user_id = None

    return JsonResponse({
        "id": question.id,
        "text": question.text,
        "user_id": user_id,
        "voting_id": voting_id,
        "answers": question.answers,
        "type": question.type
    })

# Save question 
@login_required
def save_question(request):
    if request.method != "POST":
        return error_method_not_allowed(request)
    form = QuestionForm(request.POST)
    if form.is_valid():
        if form.data['question_id']:
            question = Question.objects.filter(id=form.data['question_id']).exclude(is_active=False)
            if not len(question):
                return JsonResponse({
                    "ErrorCode": 404,
                    "Error": "InvalidQuestionId",
                })
            if not question[0].user == request.user:
                return JsonResponse({
                    "ErrorCode": 403,
                    "Error": "NotAllowedError",
                })
            if question[0].text != form.data['text'] or question[0].answers != form.data['answers']:
                Vote.objects.filter(question=question[0].id).update(is_active=False)
            question.update(text=form.data['text'], type=form.data['type'], answers=form.data['answers'])
            question = question[0]
        else:
            question = Question(text=form.data['text'], type=form.data['type'],
                                answers=form.data['answers'], voting=None, user=request.user)
            question.save()
        return JsonResponse({
            "id": question.id,
            "text": question.text,
            "type": question.type,
            "answers": question.answers,
        })
    return error_bad_request(request)

@login_required
def upload(request, upload_as="avatar"):
    if request.method != 'POST':
        return error_method_not_allowed(request)
    form = LoadImgForm(request.POST, request.FILES)
    if form.is_valid():
        role = Image.role_str_to_int(upload_as)
        image = Image(user=request.user, data=request.FILES['file'], role=role)
        image.save()
        return JsonResponse({
            "id": image.id,
            "user": image.user.id,
            "data": {
                "url": image.data.url,
            },
            "role": image.role,
            "datetime_created": image.datetime_created
        })
    return JsonResponse({'is_valid': form.is_valid(), 'errors': form.errors, 'image_data': None})

@login_required

def save_voting(request):
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
        else:
            voting = Voting.objects.filter(id=formdata['voting_id']).exclude(is_active=False)
            if not len(voting) or not voting[0].user == request.user:
                return error_forbidden(request)
            voting.update(datetime_closed=formdata['datetime_closed'],
                          title=formdata['title'],
                          open_stats=formdata['open_stats'])
            voting = voting[0]
            question_ids = []
            for question in voting.questions():
                question_ids.append(question.id)
            if question_ids != formdata['questions']:
                for question_id in question_ids:
                    Vote.objects.filter(question=question_id).update(is_active=False)
            voting.questions().update(voting=None)
        for question_id in formdata['questions']:
            Question.objects.filter(id=question_id).update(voting=voting)
        return redirect("/voting/" + str(voting.id))
    else:
        return error_bad_request(request)

@login_required
def favourites(request, action="add", voting_id=0):
    if request.method != "POST":
        return error_method_not_allowed(request)
    voting = Voting.objects.filter(id=voting_id).exclude(is_active=False)
    if len(voting):
        voting = voting[0]
        if action == "add":
            if voting.status(request.user) != voting.VOTING_BANNED and not voting.current_user_added_to_favourites(request):
                activity_item = ActivityItem(user=request.user,
                                             type=ActivityItem.ACTIVITY_FAVOURITE,
                                             voting=voting)
                activity_item.save()
                return HttpResponse(voting.favourites_count())
        elif action == "remove":
            if voting.status(request.user) != voting.VOTING_BANNED and voting.current_user_added_to_favourites(request):
                activity_item = ActivityItem.objects.filter(user=request.user.id,
                                                            type=ActivityItem.ACTIVITY_FAVOURITE,
                                                            voting=voting.id)
                activity_item.update(is_active=False)
                return HttpResponse(voting.favourites_count())
    return error_forbidden(request)

@login_required
def remove(request, model="report", id=0):
    models = {
        "comment": Comment,
        "report": Report
    }
    if not model in models:
        return error_bad_request(request)

    item = models[model].objects.filter(id=id).exclude(is_active=False)
    if not len(item) or not item[0].user == request.user:
        return error_forbidden(request)
    voting_id = item[0].voting.id
    item.update(is_active=False)
    if model == "report":
        return redirect("/profile/" + request.user.username)
    else:
        return redirect("/voting/" + str(voting_id))