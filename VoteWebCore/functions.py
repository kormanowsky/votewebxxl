from datetime import *
from dateutil import *

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

def is_logged_in(request):
    return request.user.username

def datetime_convert(dt, from_zone, to_zone):
    return dt.replace(tzinfo=from_zone).astimezone(to_zone)

def datetime_to_utc(dt):
    return datetime_convert(dt, tz.tzlocal(), tz.tzutc())

def datetime_to_local(dt):
    return datetime_convert(dt, tz.tzutc(), tz.tzlocal())

def datetime_human_diff(dt1, dt2):
    diff = dt1 - dt2
    seconds = diff.seconds
    result = ""
    if seconds >= 60*60*24:
        result += str(seconds // (60*60*24)) + "d "
        seconds = seconds % (60*60*24)
    if seconds >= 60*60:
        result += str(seconds // (60*60)) + "h "
        seconds = seconds % (60*60)
    if seconds >= 60:
        result += str(seconds // 60) + "m "
        seconds = seconds % 60
    result += str(seconds) + "s"
    return result