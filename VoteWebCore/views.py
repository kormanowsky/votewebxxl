from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from VoteWebCore.forms import *
from VoteWebCore.models import *
from VoteWebCore.functions import form_errors

# Create your views here.

register_page = {
    'Vote': 'vote',
    'login': 'login',
    'logout': 'logout',
}


@login_required
def vote_list(request):
    all_votes = TB_Vote.objects.all()
    context_votes = []
    for vote in all_votes:
        context_votes.append({
            "vote": vote, 
            "vote_test": TB_VoteDiscret.objects.filter(vote_id=vote.id)
        })
    context = {
        "vote_list": context_votes,
        "html_title": "Vote List", 
        "no_right_aside": True
    }
    return render(request, 'vote_list.html', context)


@login_required
def vote_task(request):
    context = {'is_found': False}
    vote_id = request.GET.get('vote_no', -1)
    vote_item = TB_Vote.objects.filter(id=vote_id)
    if len(vote_item) != 1:
        return render(request, 'vote_task.html', context)
    vote = vote_item[0]
    context['vote'] = vote
    context['is_found'] = True
    context['vote_type'] = vote.vote_type
    if vote.vote_type == TB_Vote.VT_DISCRET:
        context['vote_test'] = TB_VoteDiscret.objects.filter(vote_id=vote_id)
    elif vote.vote_type == TB_Vote.VT_MULTI:
        context['vote_test'] = TB_VoteMulti.objects.filter(vote_id=vote_id)  # Берем само голосование
        if len(context['vote_test']):
            vote_info = []

            ###############################################################
            # struct simple:
            # $QuestNo: {
            #            $QuestNumerate: {
            #                             'QuestText':$QuestText,
            #                              'AnswerInfo': {
            #                                              $AnswNumerate:'$AnswerText'
            #                                            }
            #                            }
            #           }
            ###############################################################

            for i in context['vote_test']:  # Начинаем брать вопросы у данного голосования
                vote_info.append({i.quests_no: {}})  # Начинаем брать информацию о вопросе у голосвания
                for quest_info in TB_VoteMulti_Quest.objects.all().filter(quests_no=i.quests_no):
                    vote_info[-1][i.quests_no] = {'QuestText': quest_info.quest_text, 'AnswerInfo': {}}
                    for quest_answ_info in TB_VoteMulti_Answer.objects.all().filter(quests_no=i.quests_no, quest_numerate=quest_info.quest_numerate):
                        vote_info[-1][i.quests_no]['AnswerInfo'][
                            quest_answ_info.answer_numerate] = quest_answ_info.answer_text
            context['vote_info'] = {int(vote_id): vote_info}
        """
        if len(context['vote_test']):
            context['vote_quests'] = []
            for i in context['vote_test']:
                i.quests = []
                i.quests.append({'vote_info': TB_VoteMulti_Quest.objects.filter(quests_no=i.quests_no)[0],
                                 'vote_answ': []})

            for i in context['vote_test']:
                for j in i['quests']:
                    j['vote_answ'].append(1)
                    # TB_VoteMulti_Quest.objects.filter(quests_no=i['quests']['vote_answ']['vote_info'].quests_no,
                    #                                  quest_numerate=i['quests']['vote_answ']['vote_info'].quest_numerate))
        """
    else:
        return render(request, 'vote_task.html', context)

    if len(context['vote_test']):
        context['is_found'] = True

    return render(request, 'vote_task.html', context)


@login_required
def vote_save(request):
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

    if len(query_vote_by_type) == 0:  # not found vote No
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'VoteNotFound'
        return JsonResponse(json_response)

    # TODO: Добавить проверку номера отвена на корректность

    # Проверка на повторное голосование, если человек уже голосовал ему будет отправлен код ошибки 2
    if len(TB_VoteLog.objects.filter(answ_user_id=request.user.id, vote_id=vote_no, vote_no=vote_quest_no)):
        json_response['ErrorCode'] = 2  # 2 - is duplicate error
    else:
        item = TB_VoteLog(vote_id=vote_no, vote_no=vote_quest_no, answer_no=int(answ_text), answ_user_id=request.user.id)
        item.save()

    return JsonResponse(json_response)


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


# New view for a single vote
@login_required
def vote(request, vote_id=-1, action="index"):
    vote_items = TB_Vote.objects.filter(id=vote_id)
    is_found = len(vote_items) == 1
    if not is_found:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "VoteNotFound"
        })
    context = {
        'vote': vote_items[0], 
        'vote_test': TB_VoteDiscret.objects.filter(vote_id=vote_id),
        'html_title': vote_items[0].vote_name
    }
    print("vote_id", vote_id, "action", action)
    return render(request, 'vote_task.html', context)


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
        "vote_list": TB_Vote.objects.filter(vote_owner=profile_owner.id),
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

def test_form(request):
    voting = Voting.objects.filter(id=1)[0]
    context = {
        "voting": voting
    }
    if request.method == "POST":
        form = VoteForm(request.POST)
        

        return render(request, "form.html", context)
    return render(request, "form.html", context)

@login_required
def save_vote_info(request):
    vote_id = int(request.GET.get('vote_id', -1))
    vote_no = int(request.GET.get('vote_no', -1))
    quest_no = int(request.GET.get('quest_no', 0))
    quest_answer = int(request.GET.get('quest_answer', 0))

    find_vote_query = TB_Vote.objects.all().filter(vote_id=vote_id)
    if not len(find_vote_query):  # not found vote
        return JsonResponse({})

    find_vote = find_vote_query[0]

    save_log = TB_VoteLog()
    save_log.answ_user_id = request.user.id
    save_log.vote_id = vote_id
    save_log.answer_no = quest_answer

    if find_vote.vote_type == find_vote.VT_DISCRET:
        save_log.vote_no = vote_no
        if 0 < quest_answer > 1:
            return JsonResponse({})

        if not len(TB_VoteDiscret.objects.all().filter(vote_id=vote_id, vote_no=vote_no)):
            return JsonResponse({})

    elif find_vote.vote_type == find_vote.VT_MULTI:
        save_log.vote_no = quest_no
        if not len(TB_VoteMulti.objects.filter(vote_id=vote_id, quests_no=vote_no)):
            return JsonResponse({})

    # todo: Check already complete
    save_log.save()
    return JsonResponse({})