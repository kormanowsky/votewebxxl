from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from VoteWebCore.models import *

# Create your views here.

register_page = {
    'Quiz': 'quiz',
    'login': 'login',
    'logout': 'logout',
}


def index(request):
    context = {}
    context['cur_page'] = request.GET.get('p', '')
    context['pages'] = register_page
    return render(request, 'index.html', context=context)


def quiz_list(request):
    context = {'quiz_list': TB_Quiz.objects.all()}
    return render(request, 'quiz_list.html', context)


def quiz_task(request):
    context = {'is_found': False}
    quiz_no = request.GET.get('quiz_no', -1)
    quiz_item = TB_Quiz.objects.filter(id=quiz_no)
    if len(quiz_item) != 1:
        return render(request, 'quiz_task.html', context)

    context['quiz_test'] = TB_QuizDiscret.objects.filter(quiz_id=quiz_no)
    print(context['quiz_test'])
    context['is_found'] = True
    return render(request, 'quiz_task.html', context)


def quiz_save(request):
    task_no = request.GET.get('task_no', '-1')
    quest_no = request.GET.get('quest_no', '-1')
    answ_text = request.GET.get('answ_text', '')
    answ_reask = request.GET.get('reask', '0')

    json_response = {'ErrorCode': 0, 'ButtonID': quest_no}

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
