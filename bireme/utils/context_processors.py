#! coding: utf-8
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

import simplejson

def additional_user_info(request):

    user = request.user
    user_role = ''
    user_cc = ''
    networks = ''
    ccs = ''
    service_role = {}
    service_list = []

    if user.is_authenticated():
        if not user.is_superuser:
            user_data = simplejson.loads(user.profile.data)
            user_cc = user_data['cc']
            networks = user_data['networks']
            ccs = user_data['ccs']

            # create a dictionary of service/role
            for sr in user_data['service_role']:
                service_id = sr.keys()[0]
                role_id = sr.values()[0]
                service_role[service_id] = role_id

                if service_id not in service_list:
                    service_list.append(service_id)

        else:
            user_cc = 'br1.1'

    return {'user_cc': user_cc, 'networks': networks, 'ccs': ccs, 'service_role': service_role,
            'user_name': user.username, 'user_id' : str(user.id), 'service_list' : service_list}

def django_settings(request):
    """
    Adds the settings specified in settings.TEMPLATE_VISIBLE_SETTINGS to
    the request context.
    """
    template_settings = {}

    for attr in getattr(settings, "TEMPLATE_VISIBLE_SETTINGS", ()):
        try:
            template_settings[attr] = getattr(settings, attr)
        except AttributeError:
            m = "TEMPLATE_VISIBLE_SETTINGS: '{0}' does not exist".format(attr)
            raise ImproperlyConfigured(m);

    return template_settings
