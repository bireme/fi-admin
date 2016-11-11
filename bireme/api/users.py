#! coding: utf-8
import requests

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


@csrf_exempt
def get_user_id(request, username):

    user_id = 'NOT FOUND'
    if username:
        try:
            user_id = User.objects.get(username=username).id
        except:
            pass

    return HttpResponse(user_id)
