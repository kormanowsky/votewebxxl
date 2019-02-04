from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from VoteWebCore.forms import *
from VoteWebCore.models import *
from VoteWebCore.functions import form_errors


@login_required
def votings(request):
    context = {
        "votings": Voting.objects.all(),
        "html_title": "Voting Library",
        "no_right_aside": True
    }
    return render(request, 'voting_library.html', context)


@login_required
def voting_task(request):
    context = {'is_found': False}
    voting_id = request.GET.get('voting_no', -1)
    voting_item = TB_Vote.objects.filter(id=voting_id)
    if len(voting_item) != 1:
        return render(request, 'voting_single.html', context)
    voting = voting_item[0]
    context['voting'] = voting
    context['is_found'] = True
    context['voting_type'] = voting.voting_type
    if voting.voting_type == TB_Vote.VT_DISCRET:
        context['voting_test'] = TB_VoteDiscret.objects.filter(voting_id=voting_id)
    elif voting.voting_type == TB_Vote.VT_MULTI:
        context['voting_test'] = TB_VoteMulti.objects.filter(voting_id=voting_id)  # Берем само голосование
        if len(context['voting_test']):
            voting_info = []

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

            for i in context['voting_test']:  # Начинаем брать вопросы у данного голосования
                voting_info.append({i.quests_no: {}})  # Начинаем брать информацию о вопросе у голосвания
                for quest_info in TB_VoteMulti_Quest.objects.all().filter(quests_no=i.quests_no):
                    voting_info[-1][i.quests_no] = {'QuestText': quest_info.quest_text, 'AnswerInfo': {}}
                    for quest_answ_info in TB_VoteMulti_Answer.objects.all().filter(quests_no=i.quests_no, quest_numerate=quest_info.quest_numerate):
                        voting_info[-1][i.quests_no]['AnswerInfo'][
                            quest_answ_info.answer_numerate] = quest_answ_info.answer_text
            context['voting_info'] = {int(voting_id): voting_info}
        """
        if len(context['voting_test']):
            context['voting_quests'] = []
            for i in context['voting_test']:
                i.quests = []
                i.quests.append({'voting_info': TB_VoteMulti_Quest.objects.filter(quests_no=i.quests_no)[0],
                                 'voting_answ': []})

            for i in context['voting_test']:
                for j in i['quests']:
                    j['voting_answ'].append(1)
                    # TB_VoteMulti_Quest.objects.filter(quests_no=i['quests']['voting_answ']['voting_info'].quests_no,
                    #                                  quest_numerate=i['quests']['voting_answ']['voting_info'].quest_numerate))
        """
    else:
        return render(request, 'voting_single.html', context)

    if len(context['voting_test']):
        context['is_found'] = True

    return render(request, 'voting_single.html', context)


@login_required
def voting_save(request):
    voting_no = int(request.GET.get('task_no', '-1'))
    voting_quest_no = int(request.GET.get('quest_no', '-1'))
    answ_text = int(request.GET.get('answ_text', '-1'))
    # answ_reask = request.GET.get('reask', '0')

    json_response = {'ErrorCode': 0, 'ButtonID': voting_quest_no}
    if not request.user.is_authenticated:
        json_response['ErrorCode'] = 403
        return JsonResponse(json_response)

    query_voting = TB_Vote.objects.filter(id=voting_no)
    if len(query_voting) == 0:  # task not found in DB
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'TaskNotFound'
        return JsonResponse(json_response)

    if query_voting[0].voting_type == query_voting[0].VT_DISCRET:
        query_voting_by_type = TB_VoteDiscret.objects.filter(voting_id=voting_no, voting_no=voting_quest_no)
    elif query_voting[0].voting_type == query_voting[0].VT_MULTI:
        query_voting_by_type = TB_VoteMulti.objects.filter(voting_id=voting_no, voting_no=voting_quest_no)
    else:
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'TaskNotFound'
        return JsonResponse(json_response)

    if len(query_voting_by_type) == 0:  # not found voting No
        json_response['ErrorCode'] = 404
        json_response['Error'] = 'VoteNotFound'
        return JsonResponse(json_response)

    # TODO: Добавить проверку номера отвена на корректность

    # Проверка на повторное голосование, если человек уже голосовал ему будет отправлен код ошибки 2
    if len(TB_VoteLog.objects.filter(answ_user_id=request.user.id, voting_id=voting_no, voting_no=voting_quest_no)):
        json_response['ErrorCode'] = 2  # 2 - is duplicate error
    else:
        item = TB_VoteLog(voting_id=voting_no, voting_no=voting_quest_no, answer_no=int(answ_text), answ_user_id=request.user.id)
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


# New view for a single voting
@login_required
def voting(request, voting_id=-1, action="index"):
    voting_items = Voting.objects.filter(id=voting_id)
    is_found = len(voting_items) == 1
    if not is_found:
        return JsonResponse({
            "ErrorCode": 404,
            "Error": "VoteNotFound"
        })
    voting = voting_items[0]
    context = {
        'voting': voting,
        'html_title': voting.title
    }
    return render(request, 'voting_single.html', context)


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
        "votings": Voting.objects.filter(owner=profile_owner.id),
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

@login_required 
def test_form(request):
    voting = Voting.objects.filter(id=1)[0]
    context = {
        "voting": voting,
        "show_form": 1
    }
    if request.method == "POST":
        if not voting.current_user_votingd(request):
            form = VoteForm(request.POST)
            answers = form.data["answers"]
            for answer in answers:
                voting = Vote(question=answer['question'], answer=answer['answer'], creator=request.user)
                voting.save()
        else:
            pass
            # TODO: Error! User cannot voting two times
        context["show_form"] = 0
    elif voting.current_user_votingd(request):
        context["show_form"] = 0
    return render(request, "form.html", context)

@login_required
def save_voting_info(request):
    voting_id = int(request.GET.get('voting_id', -1))
    voting_no = int(request.GET.get('voting_no', -1))
    quest_no = int(request.GET.get('quest_no', 0))
    quest_answer = int(request.GET.get('quest_answer', 0))

    find_voting_query = TB_Vote.objects.all().filter(voting_id=voting_id)
    if not len(find_voting_query):  # not found voting
        return JsonResponse({})

    find_voting = find_voting_query[0]

    save_log = TB_VoteLog()
    save_log.answ_user_id = request.user.id
    save_log.voting_id = voting_id
    save_log.answer_no = quest_answer

    if find_voting.voting_type == find_voting.VT_DISCRET:
        save_log.voting_no = voting_no
        if 0 < quest_answer > 1:
            return JsonResponse({})

        if not len(TB_VoteDiscret.objects.all().filter(voting_id=voting_id, voting_no=voting_no)):
            return JsonResponse({})

    elif find_voting.voting_type == find_voting.VT_MULTI:
        save_log.voting_no = quest_no
        if not len(TB_VoteMulti.objects.filter(voting_id=voting_id, quests_no=voting_no)):
            return JsonResponse({})

    # todo: Check already complete
    save_log.save()
    return JsonResponse({})