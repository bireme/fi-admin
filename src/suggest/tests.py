# coding: utf-8
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.contenttypes.models import ContentType

from utils.tests import BaseTestCase
from main.models import Resource, Keyword
from suggest.models import *


def create_test_objects():
    """
    Create objects for tests
    """

    # Create resource suggestion
    SuggestResource.objects.create(status=0, title='Sugestão de recurso',
                            link='http://bvsalud.org')

    # Create event suggestion
    SuggestEvent.objects.create(status=0, title='Sugestão de evento',
                            start_date='2014-01-01', end_date='2014-01-05',
                            link='http://bvsalud.org')

class SuggestTest(BaseTestCase):
    """
    Tests for suggest app
    """
    def setUp(self):
        super(SuggestTest, self).setUp()

        # create auxiliary models used on tests

    def test_list_resource_suggest(self):
        """
        Test list view for resource suggestions
        """
        self.login_editor()
        create_test_objects()

        # check for default list (list events of current user = 1)
        response = self.client.get('/suggested-resources/')
        self.assertContains(response, "Sugestão de recurso")
        self.assertEquals(response.context['suggestions'].count(), 1)


    # Turn off ReCaptcha validation for tests
    @override_settings(RECAPTCHA_PRIVATE_KEY='')
    def test_add_resource_suggest(self):
        """
        Test suggest_resource view
        """

        # test a invalid submition (missing field link)
        response = self.client.post('/suggest-resource', {'title': 'Sugestão de recurso'})
        self.assertContains(response,'Este campo é obrigatório.')

        # test a submition of invalid link
        response = self.client.post('/suggest-resource', {'title': 'Sugestão de recurso',
                                'link': 'XXXX'})
        self.assertContains(response,'Informe uma URL válida')


        # test a valid suggestion submition
        response = self.client.post('/suggest-resource', {'title': 'Sugestão de recurso',
                                'link': 'http://bvsalud.org'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Obrigado')


    def test_edit_resource_suggest(self):
        """
        Test edit_suggested_resource view
        """
        self.login_editor()
        create_test_objects()

        object_test = SuggestResource.objects.all()[0]
        url = '/suggested-resource/edit/{0}'.format(object_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, object_test.title)

        # Test changes values and submit
        form_data = {
                        'status': 0,
                        'title': 'Sugestão de recurso alterado',
                        'link': 'http://bvsalud.org'
                    }

        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/suggested-resources')
        self.assertContains(response, "Sugestão de recurso alterado")


    def test_list_resource_event(self):
        """
        Test list view for event suggestions
        """
        self.login_editor()
        create_test_objects()

        # check for default list (list events of current user = 1)
        response = self.client.get('/suggested-resources/?type=events')
        self.assertContains(response, "Sugestão de evento")
        self.assertEquals(response.context['suggestions'].count(), 1)


    # Turn off ReCaptcha validation for tests
    @override_settings(RECAPTCHA_PRIVATE_KEY='')
    def test_add_event_suggest(self):
        """
        Test suggest_event view
        """

        # test a invalid submition (missing field start_date and end_date)
        response = self.client.post('/suggest-event', {'title': 'Sugestão de evento'})
        self.assertContains(response,'Este campo é obrigatório.')

        # test a submition of invalid date
        response = self.client.post('/suggest-event', {'title': 'Sugestão de evento',
                                'start_date': 'XXXX', 'end_date': 'XXXX'})

        self.assertContains(response,'Informe uma data válida')

        # test a valid suggestion submition
        response = self.client.post('/suggest-event', {'title': 'Sugestão de evento',
                            'link': 'http://bvsalud.org','start_date': '21/01/2014',
                            'end_date': '27/01/2014'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Obrigado')


    def test_edit_event_suggest(self):
        """
        Test edit_suggested_event view
        """
        self.login_editor()
        create_test_objects()

        object_test = SuggestEvent.objects.all()[0]
        url = '/suggested-event/edit/{0}'.format(object_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, object_test.title)

        # Test changes values and submit
        form_data = {
                        'status': 0,
                        'title': 'Sugestão de evento alterado',
                        'link': 'http://bvsalud.org',
                        'start_date': '21/01/2014',
                        'end_date': '27/01/2014',
                    }

        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/suggested-resources')

        response = self.client.get('/suggested-resources/?type=events')
        self.assertContains(response, "Sugestão de evento alterado")


    def test_suggest_tag(self):
        """
        Test edit_suggested_event view
        """
        self.login_editor()
        resource = Resource.objects.create(status=0, title='Recurso de teste (BR1.1)',
                            link='http://bvsalud.org', originator='BIREME',
                            created_by_id=1, cooperative_center_code='BR1.1')


        form_data = {
                    'resource_id': '1',
                    'tags': 'tag1, tag2, tag3'
                    }

        response = self.client.post('/suggest-tag', form_data, follow=True)
        # check if present at keyword model 3 tags (tag1, tag2 and tag3)
        self.assertEqual(Keyword.objects.all().count(), 3)
