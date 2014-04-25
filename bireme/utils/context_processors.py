#! coding: utf-8
from django.contrib.auth.models import User

import simplejson

def additional_user_info(request):

    user = request.user
    user_role = ''
    user_cc = ''
    networks = ''
    ccs = ''

    if user.is_authenticated():
        if not user.is_superuser:
            user_data = simplejson.loads(user.profile.data)
            user_role = user_data['role'][0]
            user_cc = user_data['cc']
            networks = user_data['networks']
            ccs = user_data['ccs']
        else:
            user_role = 'admin'
            user_cc = 'br1.1'

    return { 'user_role' : user_role, 'user_cc' : user_cc, 'networks' : networks, 'ccs' : ccs, 'user_name' : user.username, 'user_id' : str(user.id)}