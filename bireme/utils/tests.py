# coding: utf-8
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from django.contrib.auth.models import User

@override_settings(AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',))
class BaseTestCase(TestCase):
    """
    This is the base test case providing commmon features for all tests acroos
    different apps in FI-ADMIN
    """
    def setUp(self):
        # set a client.
        self.client = Client()

    def login_documentalist(self):
        user_doc =  User.objects.create_user('doc', 'user@test.com', 'doc')
        user_doc.profile.data = '''
        {
            "cc" : "BR1.1",
            "user_id" : 1,
            "service_role": [
                                {"LIS" : "doc"},
                                {"DirEVE" : "doc"},
                                {"Multimedia" : "doc"},
                                {"LILDBI" : "doc"}
                            ],
            "user_name" : "Documentalist",
            "ccs" : ["BR1.1"],
            "networks" : ["NETWORK 1"]
        }
        '''
        user_doc.profile.save()

        self.client.login(username='doc', password='doc')

    def login_editor(self):
        user_editor = User.objects.create_user('editor', 'user@test.com', 'editor')
        user_editor.profile.data = '''
        {
            "cc" : "BR1.1",
            "user_id" : 1,
            "service_role": [
                                {"LIS" : "edi"},
                                {"DirEVE" : "edi"},
                                {"Multimedia" : "edi"},
                                {"LILDBI" : "edi"}
                            ],
            "user_name" : "Editor",
            "ccs" : ["BR1.1"],
            "networks" : ["NETWORK 1"]
        }
        '''
        user_editor.profile.save()

        self.client.login(username='editor', password='editor')

    def login_editor_llxp(self):
        user_editor = User.objects.create_user('editor_llxp', 'user@test.com', 'editor_llxp')
        user_editor.profile.data = '''
        {
            "cc" : "BR772",
            "user_id" : 1,
            "service_role": [
                                {"LILDBI" : "editor_llxp"}
                            ],
            "user_name" : "Editor LLXP",
            "ccs" : ["BR772"],
            "networks" : ["NETWORK 1"]
        }
        '''
        user_editor.profile.save()

        self.client.login(username='editor_llxp', password='editor_llxp')


    def login_admin(self):
        # only superuser can edit lists
        user_admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')
