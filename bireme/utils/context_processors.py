#! coding: utf-8
from django.contrib.auth.models import User

import simplejson

def additional_user_info(request):

    user = request.user
    user_role = ''
    user_cc = ''

    if user.is_authenticated():
        if not user.is_superuser:
            user_data = simplejson.loads(user.profile.data)
            user_role = user_data['role'][0]
            user_cc = user_data['cc']
        else:
            user_role = 'admin'
            user_cc = 'br1.1'

    return { 'user_role' : user_role, 'user_cc' : user_cc }