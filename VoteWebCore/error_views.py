from django.shortcuts import render

def error_bad_request(request):
    return render(request, 'error/400.html', {}, status=400)

def error_forbidden(request):
    return render(request, 'error/403.html', {}, status=403)

def error_not_found(request, exception=None):
    return render(request, 'error/404.html', {}, status=404)

def error_method_not_allowed(request):
    return render(request, 'error/405.html', {}, status=405)

def error_internal(request):
    return render(request, 'error/500.html', {}, status=500)

def error_csrf(request):
    return render(request, 'error/403.html', {}, status=403)