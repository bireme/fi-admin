# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from main.models import Descriptor
from utils.forms import BaseDescriptorInlineFormSet


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


class DescriptorFormSetTest(BaseTestCase):
    def setUp(self):
        self.DescriptorFormSet = generic_inlineformset_factory(
            Descriptor,
            formset=BaseDescriptorInlineFormSet,
            exclude=('status',),
            can_delete=True,
            extra=1
        )

    def test_duplicated(self):
        """Duplicated descriptors texts should not be accepted"""
        data = {
            'main-descriptor-content_type-object_id-TOTAL_FORMS' : '2',
            'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',
            'main-descriptor-content_type-object_id-MAX_NUM_FORMS': '',

            'main-descriptor-content_type-object_id-0-id' : '',
            'main-descriptor-content_type-object_id-0-text' : 'malaria',
            'main-descriptor-content_type-object_id-0-code' : '^d8462',
            'main-descriptor-content_type-object_id-0-status' : '0',

            'main-descriptor-content_type-object_id-1-id' : '',
            'main-descriptor-content_type-object_id-1-text' : 'malaria',
            'main-descriptor-content_type-object_id-1-code' : '^d8462',
            'main-descriptor-content_type-object_id-1-status' : '0',
        }

        formset = self.DescriptorFormSet(data)
        self.assertFalse(formset.is_valid())

    def test_unique_text(self):
        """Unique descriptors texts should validate form"""
        data = {
            'main-descriptor-content_type-object_id-TOTAL_FORMS' : '2',
            'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',
            'main-descriptor-content_type-object_id-MAX_NUM_FORMS': '',

            'main-descriptor-content_type-object_id-0-id' : '',
            'main-descriptor-content_type-object_id-0-text' : 'malaria',
            'main-descriptor-content_type-object_id-0-code' : '^d8462',
            'main-descriptor-content_type-object_id-0-status' : '0',

            'main-descriptor-content_type-object_id-1-id' : '',
            'main-descriptor-content_type-object_id-1-text' : 'ANATOMY',
            'main-descriptor-content_type-object_id-1-code' : '^d59005',
            'main-descriptor-content_type-object_id-1-status' : '0',
        }

        formset = self.DescriptorFormSet(data)
        self.assertTrue(formset.is_valid())
