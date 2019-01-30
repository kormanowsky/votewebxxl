from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

from VoteWebCore.models import *

# Create your views here.

register_page = {
    'Quiz': 'quiz',
    'login': 'login',
    'logout': 'logout',
}


@login_required
def quiz_list(request):
    all_quizzes = TB_Quiz.objects.all()
    context_quizzes = []
    for quiz in all_quizzes:
        context_quizzes.append({
            "quiz": quiz, 
            "quiz_test": TB_QuizDiscret.objects.filter(quiz_id=quiz.id)
        })
    context = {
        "quiz_list": context_quizzes,
        "html_title": "Quiz List"
    }
    return render(request, 'quiz_list.html', context)


@login_required
def quiz_task(request):
    context = {'is_found': False}
    quiz_no = request.GET.get('quiz_no', -1)
    quiz_item = TB_Quiz.objects.filter(id=quiz_no)
    if len(quiz_item) != 1:
        return render(request, 'quiz_task.html', context)
    context['quiz'] = quiz_item[0]
    context['quiz_test'] = TB_QuizDiscret.objects.filter(quiz_id=quiz_no)
    print(context['quiz_test'])
    print(quiz_item[0].quiz_owner)
    context['is_found'] = True
    return render(request, 'quiz_task.html', context) 


@login_required
def quiz_save(request):
    task_no = request.GET.get('task_no', '-1')
    quest_no = request.GET.get('quest_no', '-1')
    answ_text = request.GET.get('answ_text', '')
    # answ_reask = request.GET.get('reask', '0')

    json_response = {'ErrorCode': 0, 'ButtonID': quest_no}
    if not request.user.is_authenticated:
        json_response['ErrorCode'] = 403
        return JsonResponse(json_response)

    if len(TB_Quiz.objects.filter(id=task_no)) == 0:  # task not found in DB
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'TaskNotFound'
        return JsonResponse(json_response)

    if len(TB_QuizDiscret.objects.filter(quiz_no=quest_no)) == 0:  # not found quiz No
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'QuizNotFound'
        return JsonResponse(json_response)

    item = TB_QuizLog(quiz_id=task_no, quiz_no=quest_no, result_text=answ_text, answ_user_id=1)
    item.save()
    return JsonResponse(json_response)


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login')


def register(request):
    context = {'form': UserCreationForm(request.POST)}
    if context['form'].is_valid():
        context['form'].save()
        return HttpResponseRedirect('/login')
    return render(request, 'registration/registration.html', context)


# New view for a single quiz
@login_required
def quiz(request, quiz_id=-1, action="index"):
    quiz_items = TB_Quiz.objects.filter(id=quiz_id)
    is_found = len(quiz_items) == 1
    if not is_found:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "QuizNotFound"
        })
    context = {
        'quiz': quiz_items[0], 
        'quiz_test': TB_QuizDiscret.objects.filter(quiz_id=quiz_id),
        'html_title': quiz_items[0].quiz_name
    }
    print("quiz_id", quiz_id, "action", action)
    return render(request, 'quiz_task.html', context)


def profile(request, username=None):
    if username is None:
        if request.user.username:
            username = request.user.username
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
        "quiz_list": TB_Quiz.objects.filter(quiz_owner=profile_owner.id),
        "no_right_aside": True,
    }
    return render(request, 'profile.html', context)