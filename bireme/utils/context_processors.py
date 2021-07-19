#! coding: utf-8
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

import simplejson

def additional_user_info(request):

    user = request.user
    user_role = ''
    user_type = ''
    user_cc = ''
    networks = ''
    ccs = ''
    service_role = {}
    service_list = []
    ccs_by_network = []

    if user.is_authenticated():
        if user.profile.data:
            user_data = simplejson.loads(user.profile.data)
            user_cc = user_data.get('cc')
            networks = user_data.get('networks')
            ccs = user_data.get('ccs')
            ccs_by_network = user_data.get('ccs_by_network')
            user_type = user_data.get('user_type')

            # create a dictionary of service/role
            for sr in user_data['service_role']:
                service_id = sr.keys()[0]
                role_id = sr.values()[0]
                service_role[service_id] = role_id

                if service_id not in service_list:
                    service_list.append(service_id)

    return {'user_cc': user_cc, 'user_type': user_type, 'user_name': user.username, 'user_id' : str(user.id),
            'networks': networks, 'ccs': ccs, 'ccs_by_network': ccs_by_network, 'service_role': service_role, 'service_list' : service_list}

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
