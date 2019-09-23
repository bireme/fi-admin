# coding: utf-8
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from model_mommy import mommy

from main.models import *
from utils.models import Country
from utils.tests import BaseTestCase


def minimal_form_data():
    """
    Define a minimal fields for submit a form
    """

    form_data = {
        'status': '0',
        'title': 'Recurso de teste',
        'description': 'Recurso para testes',
        'abstract': 'Resumo',

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-keyword-content_type-object_id-TOTAL_FORMS': '0',
        'main-keyword-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',
    }

    return form_data


def complete_form_data():
    """
    Define missing fields for a valid submission
    """

    missing_fields = {
        'link'  : 'http://bvsalud.org',
        'originator'  : 'BIREME',
        'source_type': 1,
        'source_language': 1,
        'originator_location'  : 1,

        'main-descriptor-content_type-object_id-TOTAL_FORMS' : '1',

        'main-descriptor-content_type-object_id-0-id' : '',
        'main-descriptor-content_type-object_id-0-text' : 'malaria',
        'main-descriptor-content_type-object_id-0-code' : '^d8462',
        'main-descriptor-content_type-object_id-0-status' : '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS' : '1',
        'main-resourcethematic-content_type-object_id-0-thematic_area' : '1',
        'main-resourcethematic-content_type-object_id-0-status' : '0',
    }

    complete_form_data = minimal_form_data()
    complete_form_data.update(missing_fields)

    return complete_form_data


def create_resource_object():
    """
    Create resource object for tests
    """

    # Create two objects of different users and same center code
    Resource.objects.create(status=0, title='Recurso de teste (BR1.1)',
                            link='http://bvsalud.org', originator='BIREME',
                            created_by_id=1, cooperative_center_code='BR1.1')

    Resource.objects.create(status=0, title='Recurso de teste (BR1.1)',
                            link='http://bvsalud.org', originator='BIREME',
                            created_by_id=2, cooperative_center_code='BR1.1')

    # Create one object of diffent center code
    Resource.objects.create(status=0, title='Recurso de teste (PY3.1)',
                            link='http://bvsalud.org', originator='BIREME',
                            created_by_id=3, cooperative_center_code='PY3.1')


    # add descriptor and thematic area for resource pk 1
    object_ct = ContentType.objects.get_for_model(Resource)
    descriptor = Descriptor.objects.create(object_id=1, content_type=object_ct, text='descritor 1')
    keyword = Keyword.objects.create(object_id=1, content_type=object_ct, text='keyword 1')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=object_ct, thematic_area_id=1)


class ResourceTest(BaseTestCase):
    """
    Tests for resource app
    """
    def setUp(self):
        super(ResourceTest, self).setUp()

        # create auxiliary models used on tests
        SourceType.objects.create(acronym='database', name='Base de dados')
        SourceLanguage.objects.create(acronym='pt-br', name='português')
        Country.objects.create(code='BR', name='Brasil')
        ThematicArea.objects.create(acronym='LISBR1.1', name='Enfermagem')


    def test_list_resource(self):
        """
        Test list resources
        """
        self.login_editor()
        create_resource_object()

        # check for default list (list resources of current user = 1)
        response = self.client.get('/resources/')
        self.assertContains(response, "Recurso de teste (BR1.1)")
        self.assertEquals(response.context['resources'].count(), 1)

        # default list don't show resources from other users
        self.assertNotContains(response, "Recurso de teste (PY3.1)")

        # check for list of all resources
        response = self.client.get('/resources/?filter_owner=*')
        total_of_resources = Resource.objects.all().count()
        self.assertEquals(response.context['resources'].count(), total_of_resources)


    def test_add_resource(self):
        """
        Tests of create view
        """
        self.login_editor()

        # invalid submission with missing required fields
        form_data = minimal_form_data()
        response = self.client.post('/resource/new', form_data )

        self.assertContains(response,'Por favor verifique os campos obrigatórios')
        self.assertContains(response,'Você precisa inserir pelo menos um descritor de assunto')
        self.assertContains(response,'Você precisa selecionar pelo menos uma área temática')

        # complete form_data with required fields and re-submit form
        form_data = complete_form_data()

        # test valid submission
        # after submit a valid content the view will redirect to /resources and list the objects
        # follow=True will allow check if the new data is on the list
        response = self.client.post('/resource/new', form_data, follow=True)

        self.assertRedirects(response, '/resources')
        self.assertContains(response, "Recurso de teste")

        # check if is set cooperative center code of user (editor = BR1.1)
        self.assertEquals(Resource.objects.all()[0].cooperative_center_code, "BR1.1")


    def test_edit_resource(self):
        """
        Tests edit resource
        """
        self.login_editor()
        create_resource_object()

        resource_test = Resource.objects.all()[0]
        url = '/resource/edit/{0}'.format(resource_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, resource_test.title)

        # Test changes values and submit
        form_data = complete_form_data()

        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/resources')
        self.assertContains(response, "Recurso de teste")

    def test_delete_resource(self):
        """
        Tests delete resource
        """
        self.login_editor()
        create_resource_object()

        form_data = {'delete_id': '1'}

        response = self.client.post('/resources', form_data, follow=True)
        self.assertTrue(Resource.objects.filter(id=1).count() == 0)

        # check delete of related objects (descriptors, thematic_area, keywords)
        object_ct = ContentType.objects.get_for_model(Resource)

        self.assertTrue(Descriptor.objects.filter(object_id=1, content_type=object_ct).count() == 0)
        self.assertTrue(Keyword.objects.filter(object_id=1, content_type=object_ct).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=1, content_type=object_ct).count() == 0)


    def test_list_source_type(self):
        """
        Tests list source type
        """

        # check if documentalist has access to list view
        self.login_documentalist()
        response = self.client.get('/types/' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        response = self.client.get('/types/')
        self.assertContains(response, "Base de dados")


    def test_add_source_type(self):
        """
        Tests create source type
        """
        # check if documentalist has access to create form
        self.login_documentalist()
        response = self.client.get('/type/new' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        form_data = {
            'status': '0',
            'acronym': 'site',
            'name': 'Website',
            'language' : 'pt-br',
            'sourcetypelocal_set-TOTAL_FORMS': '0',
            'sourcetypelocal_set-INITIAL_FORMS': '0',
        }

        response = self.client.post('/type/new', form_data, follow=True )

        self.assertRedirects(response, '/types')
        self.assertContains(response, "Website")

    def test_list_source_language(self):
        """
        Tests list source language
        """

        # check if documentalist has access to the list view
        self.login_documentalist()
        response = self.client.get('/languages/' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        response = self.client.get('/languages/')
        self.assertContains(response, "português")


    def test_add_source_language(self):
        """
        Tests create source language
        """
        # check if documentalist has access to create form
        self.login_documentalist()
        response = self.client.get('/language/new' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        form_data = {
            'status': '0',
            'acronym': 'en-us',
            'name': 'Inglês',
            'language' : 'pt-br',
            'sourcelanguagelocal_set-TOTAL_FORMS': '0',
            'sourcelanguagelocal_set-INITIAL_FORMS': '0',
        }

        response = self.client.post('/language/new', form_data, follow=True )

        self.assertRedirects(response, '/languages')
        self.assertContains(response, "Inglês")


    def test_search_by_id(self):
        self.login_documentalist()
        mommy.make(Resource, id=1)

        response = self.client.get("/resources", {"s": "id:1", "filter_owner": "*"})

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<a href="/resource/edit/1">1</a')

        response = self.client.get("/resources", {"s": "id:2", "filter_owner": "*"})
        self.assertNotContains(response, '<a href="/resource/edit/1">1</a')
