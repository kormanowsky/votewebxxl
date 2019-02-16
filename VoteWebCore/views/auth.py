from django.contrib import auth, messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.shortcuts import render, redirect

from VoteSimple.settings import LOGIN_REDIRECT_URL
from VoteWebCore.forms import RegisterForm
from VoteWebCore.functions import form_errors


# Auth views


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid() or form.get_user() is None:
            messages.add_message(request, messages.ERROR, 'Authentication data is empty or incorrect')
        else:
            auth.login(request, form.get_user())
            next = request.GET.get('next', LOGIN_REDIRECT_URL)
            return redirect(next)
        return render(request, 'login.html', context=csrf(request))
    if request.user.is_authenticated:
        return redirect(LOGIN_REDIRECT_URL)
    else:
        after = request.GET.get('after', '')
        if len(after):
            if after == "logout":
                message = "You logged out."
            elif after == "register":
                message = 'Your registration process has finished successfully. You may now log in.'
            else:
                message = ""
            if len(message):
                messages.add_message(request, messages.SUCCESS, message)
        return render(request, 'login.html', context=csrf(request))


def logout(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    auth_logout(request)
    return redirect('/login?after=logout')


def register(request):
    context = {
        'form': RegisterForm(request.POST)
    }
    if request.method == "POST":
        if context['form'].is_valid():
            context['form'].save()
            return redirect('/login?after=register')
        else:
            for error in form_errors(context['form']):
                messages.add_message(request, messages.ERROR, error)
    return render(request, 'registration.html', context)


def remove_account(request):
    if not request.user.is_authenticated:
        return redirect('/login')
    request.user.is_active = False
    request.user.save()
    auth_logout(request)
    return render(request, "remove_account.html", {
        "html_title": "Remove Account"
    })
