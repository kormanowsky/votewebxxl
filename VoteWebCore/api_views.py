from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from VoteWebCore.models import *
from VoteWebCore.forms import *

# Get one question
def get_question(request, id=0):
    question = Question.objects.filter(id=id)
    if not len(question):
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "InvalidQuestionId",
        })
    question = question[0]

    if question.voting is not None:
        voting_id = question.voting.id
    else:
        voting_id = None
    if question.owner is not None:
        owner_id = question.owner.id
    else:
        owner_id = None

    return JsonResponse({
        "id": question.id,
        "text": question.text,
        "owner_id": owner_id,
        "voting_id": voting_id,
        "answers": question.answers,
        "type": question.type
    })

# Save question 
@login_required
def save_question(request):
    if request.method != "POST":
        return JsonResponse({
            "ErrorCode": 403, 
            "Error": "NotAllowedMethodError"
        })
    form = QuestionForm(request.POST)
    if form.is_valid():
        if form.data['question_id']:
            question = Question.objects.filter(id=form.data['question_id'])
            if not len(question):
                return JsonResponse({
                    "ErrorCode": 404,
                    "Error": "InvalidQuestionId",
                })
            if not question[0].owner == request.user:
                return JsonResponse({
                    "ErrorCode": 403,
                    "Error": "NotAllowedError",
                })
            if question.text != form.data['text'] or question.answers != form.data['answers']:
                Vote.objects.filter(question=question.id).delete()
            question.update(text=form.data['text'], type=form.data['type'], answers=form.data['answers'])
            question = question[0]
        else:
            question = Question(text=form.data['text'], type=form.data['type'],
                                answers=form.data['answers'], voting=None, owner=request.user)
            question.save()
        return JsonResponse({
            "id": question.id,
            "text": question.text,
            "type": question.type,
            "answers": question.answers,
        })
    return JsonResponse({
        "ErrorCode": 403,
        "Error": "InvalidInputError",
    })

@login_required
def upload(request, upload_as="avatar"):
    if request.method == 'POST':
        form = LoadImgForm(request.POST, request.FILES)
        if form.is_valid():
            role = Image.role_str_to_int(upload_as)
            image = Image(owner=request.user, data=request.FILES['file'], role=role)
            image.save()
            return JsonResponse({
                "id": image.id,
                "owner": image.owner.id,
                "data": {
                    "url": image.data.url,
                },
                "role": image.role,
                "datetime_created": image.datetime_created
            })
    else:
        return JsonResponse({'is_valid': False, 'errors': {'method': 'Method must be POST'}})
    return JsonResponse({'is_valid': form.is_valid(), 'errors': form.errors, 'image_data': None})