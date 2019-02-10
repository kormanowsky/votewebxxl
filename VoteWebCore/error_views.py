from django.shortcuts import render


# Error handlers


def error_bad_request(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 400,
        "text": "Bad Request"
    }, status=400)


def error_forbidden(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 403,
        "text": "Forbidden"
    }, status=403)


def error_not_found(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 404,
        "text": "Not Found"
    }, status=404)


def error_method_not_allowed(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 405,
        "text": "Method Not Allowed"
    }, status=405)


def error_internal(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 500,
        "text": "Internal Server Error"
    }, status=500)


def error_csrf(request, *args, **kwargs):
    return render(request, 'error.html', {
        "code": 403,
        "text": "Forbidden"
    }, status=403)
