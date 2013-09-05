from django.http import Http404
from functools import wraps

def advanced_permission(method):
    @wraps(method)
    def wrapper(request, *args, **kwargs):

        user = request.user
        if not user.is_superuser and user.profile.type == "basic":
            raise Http404

        return method(request, *args, **kwargs)
    return wrapper

def superuser_permission(method):
    @wraps(method)
    def wrapper(request, *args, **kwargs):

        user = request.user
        if not user.is_superuser:
            raise Http404

        return method(request, *args, **kwargs)
    return wrapper