from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

from .error import *
from VoteWebCore.forms import *


# Get one question
def get_question(request, question_id=0):
    question = Question.objects.filter(id=question_id).exclude(is_active=False)

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

    if question.image is not None:
        image = {
            "id": question.image.id,
            "data": {
                "url": question.image.data.url,
            }
        }
    else:
        image = None

    return JsonResponse({
        "id": question.id,
        "text": question.text,
        "user_id": user_id,
        "voting_id": voting_id,
        "answers": question.answers,
        "type": question.type,
        "image": image,
    })


# Save question
@login_required
def save_question(request):
    if request.method != "POST":
        return error_method_not_allowed(request)

    form = QuestionForm(request.POST)
    if form.is_valid():
        # Question update
        if form.data['question_id']:
            question = Question.objects.filter(id=form.data['question_id']).exclude(is_active=False)
            if not len(question):
                return error_bad_request(request)
            if not question[0].user == request.user:
                return error_forbidden(request)
            # If question text or question answers changed, we remove all votes of this question
            if question[0].text != form.data['text'] or question[0].answers != form.data['answers']:
                Vote.objects.filter(question=question[0].id).update(is_active=False)

            question.update(text=form.data['text'], type=form.data['type'], answers=form.data['answers'])
            question = question[0]
        # New question
        else:
            question = Question(text=form.data['text'], type=form.data['type'],
                                answers=form.data['answers'], voting=None, user=request.user)
            question.save()

        # Question image
        if form.data['image_id']:
            image = Image.objects.filter(id=form.data['image_id']).exclude(is_active=False)
            if not len(image):
                return error_bad_request(request)
            if not image[0].user == request.user:
                return error_forbidden(request)
            image = image[0]
        else:
            image = None
        question.image = image
        question.save()

        return JsonResponse({
            "html": render_to_string(request=request,
                                     context={"question": question},
                                     template_name="question_small.html"),
            "id": question.id,
        })
    return error_bad_request(request)


# Upload file
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
    return error_bad_request(request)


# Add to favourites or remove from favourites
@login_required
def favourites(request, action="add", voting_id=0):
    if request.method != "POST":
        return error_method_not_allowed(request)

    voting = Voting.objects.filter(id=voting_id).exclude(is_active=False)
    if len(voting):
        voting = voting[0]
        if action == "add":
            if voting.current_user_added_to_favourites(request):
                return error_forbidden(request)
            if voting.status(request.user) != voting.VOTING_BANNED:
                activity_item = ActivityItem(user=request.user,
                                             type=ActivityItem.ACTIVITY_FAVOURITE,
                                             voting=voting)
                activity_item.save()
                return HttpResponse(voting.favourites_count())
            return error_forbidden(request)
        elif action == "remove":
            if not voting.current_user_added_to_favourites(request):
                return error_forbidden(request)
            if voting.status(request.user) != voting.VOTING_BANNED:
                activity_item = ActivityItem.objects.filter(user=request.user.id,
                                                            type=ActivityItem.ACTIVITY_FAVOURITE,
                                                            voting=voting.id)
                activity_item.update(is_active=False)
                return HttpResponse(voting.favourites_count())
            return error_forbidden(request)
    return error_bad_request(request)


# Remove reports and comments
@login_required
def remove(request, model="report", model_id=0):
    model_classes = {
        "comment": Comment,
        "report": Report
    }
    if model not in model_classes:
        return error_bad_request(request)

    item = model_classes[model].objects.filter(id=model_id).exclude(is_active=False)

    if not len(item):
        return error_bad_request(request)

    item = item[0]

    if not item.user == request.user:
        return error_forbidden(request)

    item.is_active = False
    item.save()
    voting = item.voting

    if model == "report":
        voting.banned = 0
        voting.save()
        return redirect("/profile/{}?after=remove_report&report_id={}".format(request.user.username, item.id))
    else:
        return redirect("/voting/{}?after=remove_comment&comment_id={}".format(voting.id, item.id))
