from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

from VoteWebCore.models import *

# from django.db.models import Q

# Create your views here.

register_page = {
    'Quiz': 'quiz',
    'login': 'login',
    'logout': 'logout',
}


@login_required
def quiz_list(request):
    context = {'quiz_list': TB_Vote.objects.all()}
    """ Not Work!!!!!!
    for i in context['quiz_list']:
        quiz_info = TB_QuizDiscret.objects.filter(quiz_id=context['quiz_list'][i]['id'])
        complete_quiz_info = TB_QuizLog.objects.filter(quiz_id=context['quiz_list'][i]['id'], answ_user_id=request.user.id)
        if quiz_info.size() == complete_quiz_info.size():
            print('!!!!!')
    """
    return render(request, 'quiz_list.html', context)


@login_required
def quiz_task(request):
    context = {'is_found': False}
    quiz_no = request.GET.get('quiz_no', -1)
    quiz_item = TB_Vote.objects.filter(id=quiz_no)
    if len(quiz_item) != 1:
        return render(request, 'quiz_task.html', context)

    context['quiz_test'] = TB_VoteDiscret.objects.filter(quiz_id=quiz_no)
    print(context['quiz_test'])
    context['is_found'] = True
    return render(request, 'quiz_task.html', context)


@login_required
def quiz_save(request):
    vote_no = int(request.GET.get('task_no', '-1'))
    vote_quest_no = int(request.GET.get('quest_no', '-1'))
    answ_text = int(request.GET.get('answ_text', '-1'))
    # answ_reask = request.GET.get('reask', '0')

    json_response = {'ErrorCode': 0, 'ButtonID': vote_quest_no}
    if not request.user.is_authenticated:
        json_response['ErrorCode'] = 403
        return JsonResponse(json_response)

    query_vote = TB_Vote.objects.filter(id=vote_no)
    if len(query_vote) == 0:  # task not found in DB
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'TaskNotFound'
        return JsonResponse(json_response)

    if query_vote[0].vote_type == query_vote[0].VT_DISCRET:
        query_vote_by_type = TB_VoteDiscret.objects.filter(vote_id=vote_no, vote_no=vote_quest_no)
    elif query_vote[0].vote_type == query_vote[0].VT_MULTI:
        query_vote_by_type = TB_VoteMulti.objects.filter(vote_id=vote_no, vote_no=vote_quest_no)
    else:
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'TaskNotFound'
        return JsonResponse(json_response)

    if len(query_vote_by_type) == 0:  # not found quiz No
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'QuizNotFound'
        return JsonResponse(json_response)

    # TODO: Добавить проверку номера отвена на корректность

    # Проверка на повторное голосование, если человек уже голосовал ему будет отправлен код ошибки 2
    if len(TB_VoteLog.objects.filter(answ_user_id=request.user.id, quiz_id=vote_no, quiz_no=vote_quest_no)):
        json_response['ErrorCode'] = 2  # 2 - is duplicate error
    else:
        item = TB_VoteLog(quiz_id=vote_no, quiz_no=vote_quest_no, result_text=answ_text, answ_user_id=request.user.id)
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
