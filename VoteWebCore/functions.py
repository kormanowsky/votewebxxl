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


def generate_file_name(src_name):
    str_ret = ''
    from random import randint
    for _ in range(1, 16):
        str_ret += str(randint(1, 99))  # generate random name
    str_ret += '.' + src_name.split('.')[-1]  # get source file type
    return str_ret


def save_upload_file(f, file_path='VoteWebCore/static/img/'):
    ret_data = {'path': file_path, 'file_name': generate_file_name(f._name)}
    with open(ret_data['path'] + ret_data['file_name'], 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return ret_data


def file_to_base64(f):
    import base64

    img_byte = b''
    for chunk in f.chunks():
        img_byte += chunk

    return base64.b64encode(img_byte)
