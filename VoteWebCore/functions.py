from dateutil import *
from random import randint
from uuid import uuid4
from datetime import *

from django.utils.safestring import mark_safe
from django.utils.html import format_html

from VoteWebCore.models import *


# Useful functions
def form_errors(form):
    errors_str = form.errors.as_text()
    _errors = errors_str.split('*')
    errors = []
    for i in range(len(_errors)):
        err = _errors[i].strip()
        if len(err) and err[0].isupper():
            errors.append(err)
    return errors


def datetime_convert(dt, from_zone, to_zone):
    return dt.replace(tzinfo=from_zone).astimezone(to_zone)


def datetime_to_utc(dt):
    return datetime_convert(dt, tz.tzlocal(), tz.tzutc())


def datetime_to_local(dt):
    return datetime_convert(dt, tz.tzutc(), tz.tzlocal())


def datetime_human_diff(dt1, dt2):
    if dt1 < dt2:
        dt1, dt2 = dt2, dt1
    diff = dt1 - dt2
    seconds = round(diff.total_seconds())
    result = ""
    if seconds >= 60 * 60 * 24:
        result += str(seconds // (60 * 60 * 24)) + "d "
        seconds = seconds % (60 * 60 * 24)
    if seconds >= 60 * 60:
        result += str(seconds // (60 * 60)) + "h "
        seconds = seconds % (60 * 60)
    if seconds >= 60:
        result += str(seconds // 60) + "m "
        seconds = seconds % 60
    result += str(seconds) + "s"
    return result

def datetime_str_to_obj(datetime_str):
    if len(datetime_str.split(".")) != 3:
        return None
    day, month, year = list(map(int, datetime_str.split(".")))
    datetime_obj = datetime(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0,
                               tzinfo=tz.tzutc())
    return datetime_obj

def datetime_human(dt):
    return dt.strftime("%d.%m.%Y at %H:%M")

def date_human(dt):
    return dt.strftime("%d.%m.%Y")

def generate_file_name(file, src_name):
    return str(uuid4()).replace("-", "/") + '.' + src_name.split('.')[-1]


# User html for admin page
def user_html(user):
    if not isinstance(user, User):
        return "-"
    return format_html('<a href="/admin/auth/user/{0}/change/">{1} {2}</a><br/>@{3}',
                       mark_safe(user.id),
                       mark_safe(user.first_name),
                       mark_safe(user.last_name),
                       mark_safe(user.username))


# Voting html for admin page
def voting_html(voting):
    if not voting:
        return "-"
    return format_html('<a href="/admin/VoteWebCore/voting/{0}/change">{1} (#{0})</a><br/>',
                       mark_safe(voting.id),
                       mark_safe(voting.title))


# Internal method for question html
def _question_html():
    return '<a href="/admin/VoteWebCore/question/{0}/change">{1} (#{0})</a><br/>'


# Question html for admin page
def question_html(question):
    if not question:
        return "-"
    return format_html(_question_html(),
                       mark_safe(question.id),
                       mark_safe(question.text))


# Questions html for admin page
def questions_html(questions):
    if not len(questions):
        return "-"
    html = ""
    for question in questions:
        html += _question_html().format(question.id, question.text)
    return mark_safe(html)