from django.http import HttpResponseForbidden
from functools import wraps

def advanced_permission(method):
    @wraps(method)
    def wrapper(request, *args, **kwargs):

        user = request.user
        if not user.is_superuser and user.profile.type == "basic":
            return HttpResponseForbidden()

        return method(request, *args, **kwargs)
    return wrapper

def superuser_permission(method):
    @wraps(method)
    def wrapper(request, *args, **kwargs):

        user = request.user
        if not user.is_superuser:
            return HttpResponseForbidden()

        return method(request, *args, **kwargs)
    return wrapper