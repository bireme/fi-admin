# coding: utf-8
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from main.models import Descriptor
from utils.betterforms import BetterModelForm, Fieldset, FieldsetCollection
from utils.forms import BaseDescriptorInlineFormSet


@override_settings(AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',))
class BaseTestCase(TestCase):
    """
    This is the base test case providing commmon features for all tests acroos
    different apps in FI-ADMIN
    """
    @classmethod
    def tearDownClass(cls):
        try:
            super().tearDownClass()
        except AttributeError:
            pass

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
        return user_doc

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
        return user_editor

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
        return user_editor

    def login_admin(self):
        # only superuser can edit lists
        user_admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        user_admin.profile.data = '''
        {
            "cc" : "BR1.1",
            "user_id" : 1,
            "service_role": [
                                {"LIS" : "admin"},
                                {"DirEVE" : "admin"},
                                {"Multimedia" : "admin"},
                                {"LILDBI" : "admin"},
                                {"LeisRef" : "admin"},
                                {"DirIns" : "admin"}
                            ],
            "user_name" : "Admin",
            "ccs" : ["BR1.1"],
            "networks" : ["NETWORK 1"]
        }
        '''
        user_admin.profile.save()
        self.client.login(username='admin', password='admin')
        return user_admin


class _DummyForm(forms.Form):
    title = forms.CharField()
    author = forms.CharField()
    status = forms.IntegerField()
    notes = forms.CharField(required=False)


class FieldsetTest(TestCase):

    def _make_form(self, **kwargs):
        return _DummyForm(data={'title': 'Test', 'author': 'Auth', 'status': '1', 'notes': ''}, **kwargs)

    def test_fieldset_yields_bound_fields_for_defined_fields(self):
        form = self._make_form()
        fs = Fieldset(form, 'general', fields=['title', 'author'])
        bound = list(fs)
        self.assertEqual(len(bound), 2)
        self.assertEqual(bound[0].name, 'title')
        self.assertEqual(bound[1].name, 'author')

    def test_fieldset_skips_fields_not_in_form(self):
        form = self._make_form()
        fs = Fieldset(form, 'general', fields=['title', 'nonexistent'])
        bound = list(fs)
        self.assertEqual(len(bound), 1)
        self.assertEqual(bound[0].name, 'title')

    def test_fieldset_adds_row_attrs(self):
        form = self._make_form()
        fs = Fieldset(form, 'general', fields=['title'])
        bound = list(fs)
        self.assertTrue(hasattr(bound[0], 'row_attrs'))

    def test_fieldset_attributes(self):
        form = self._make_form()
        fs = Fieldset(form, 'meta', fields=['status'], legend='Metadata', classes=['collapse', 'extra'], description='Status info')
        self.assertEqual(fs.name, 'meta')
        self.assertEqual(fs.legend, 'Metadata')
        self.assertEqual(fs.classes, 'collapse extra')
        self.assertEqual(fs.description, 'Status info')

    def test_fieldset_classes_as_string(self):
        form = self._make_form()
        fs = Fieldset(form, 'meta', fields=[], classes='single-class')
        self.assertEqual(fs.classes, 'single-class')


class FieldsetCollectionTest(TestCase):

    def _make_form(self):
        return _DummyForm(data={'title': 'T', 'author': 'A', 'status': '1', 'notes': ''})

    def test_iteration_yields_fieldsets(self):
        form = self._make_form()
        fieldsets_def = [
            ('general', {'fields': ['title', 'author'], 'legend': 'General'}),
            ('extra', {'fields': ['notes'], 'legend': 'Extra', 'classes': ['collapse']}),
        ]
        collection = FieldsetCollection(form, fieldsets_def)
        fieldsets = list(collection)
        self.assertEqual(len(fieldsets), 2)
        self.assertEqual(fieldsets[0].name, 'general')
        self.assertEqual(fieldsets[0].legend, 'General')
        self.assertEqual(fieldsets[1].name, 'extra')
        self.assertEqual(fieldsets[1].classes, 'collapse')

    def test_empty_fieldsets(self):
        form = self._make_form()
        collection = FieldsetCollection(form, None)
        self.assertEqual(list(collection), [])

    def test_fieldset_collection_fields_are_iterable(self):
        form = self._make_form()
        fieldsets_def = [
            ('general', {'fields': ['title', 'status']}),
        ]
        collection = FieldsetCollection(form, fieldsets_def)
        fieldsets = list(collection)
        bound = list(fieldsets[0])
        self.assertEqual(len(bound), 2)
        self.assertEqual(bound[0].name, 'title')
        self.assertEqual(bound[1].name, 'status')


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


class GetFieldDisplayTest(TestCase):
    """Regression tests for the get_field_display template tag (SelectMultiple branch)"""

    def setUp(self):
        from title.models import Title
        from utils.models import Country

        self.brazil = Country.objects.create(code='BR', name='Brazil')
        self.chile = Country.objects.create(code='CL', name='Chile')
        self.peru = Country.objects.create(code='PE', name='Peru')

        class CountryForm(forms.ModelForm):
            class Meta:
                model = Title
                fields = ('country',)

        self.CountryForm = CountryForm

    def _render(self, form, sep=', '):
        from django.template import Context, Template

        template = Template(
            "{% load app_filters %}{% get_field_display form.instance field sep %}"
        )
        field = form['country']
        return template.render(Context({'form': form, 'field': field, 'sep': sep}))

    def test_display_selected_options(self):
        """Only the selected options should be displayed, separated by sep"""
        form = self.CountryForm(data={'country': [str(self.brazil.pk), str(self.peru.pk)]})
        self.assertTrue(form.is_valid())
        out = self._render(form)
        self.assertEqual(out, '%s, %s' % (self.brazil, self.peru))
        self.assertNotIn(str(self.chile), out)

    def test_display_single_selected_option(self):
        form = self.CountryForm(data={'country': [str(self.chile.pk)]})
        self.assertTrue(form.is_valid())
        self.assertEqual(self._render(form), str(self.chile))

    def test_display_no_selection(self):
        form = self.CountryForm(data={'country': []})
        self.assertEqual(self._render(form), '')
