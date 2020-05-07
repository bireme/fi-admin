#! coding: utf-8
from django.conf import settings
from django.contrib.auth.models import User
import requests
import json
from django.contrib.sessions.backends.db import SessionStore, Session

class EmailModelBackend(object):

    def authenticate(self, username=None, password=None):

        # caso seja superuser, ele loga com o login padrão do django
        try:
            user = User.objects.get(username=username)
            if user.is_superuser:
                if user.check_password(password):
                    return user
        except:
            pass

        # url
        api_uri = "%s/api/auth/login/" % settings.BIREMELOGIN_BASE_URL

        data = {'username': username, 'password': password, 'format': 'json', 'service': settings.BIREMELOGIN_SERVICE}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        r = requests.post(api_uri, data=json.dumps(data), headers=headers, verify=False)
        response = json.loads(r.text)

        if 'success' in response and response['success'] == True:
            # use username returned by accounts to avoid duplication if user is login with email
            username = response['data'].get('user')
            user, created = User.objects.get_or_create(username=username[:30])
            user.is_staff = True
            user.save()

            # load and save user profile in json format
            data = json.dumps(response['data'])
            user.profile.data = data
            user.profile.save()

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
