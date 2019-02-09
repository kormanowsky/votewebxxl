from django.shortcuts import render

# Error handlers


def error_bad_request(request):
    return render(request, 'error.html', {
        "code": 400,
        "text": "Bad Request"
    }, status=400)


def error_forbidden(request):
    return render(request, 'error.html', {
        "code": 403,
        "text": "Forbidden"
    }, status=403)


def error_not_found(request, exception=None):
    return render(request, 'error.html', {
        "code": 404,
        "text": "Not Found"
    }, status=404)


def error_method_not_allowed(request):
    return render(request, 'error.html', {
        "code": 405,
        "text": "Method Not Allowed"
    }, status=405)


def error_internal(request):
    return render(request, 'error.html', {
        "code": 500,
        "text": "Internal Server Error"
    }, status=500)


def error_csrf(request):
    return render(request, 'error.html', {
        "code": 403,
        "text": "Forbidden"
    }, status=403)