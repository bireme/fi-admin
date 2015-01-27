# coding: utf-8

from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from main.models import Descriptor, ResourceThematic, ThematicArea

from utils.tests import BaseTestCase
from models import *

def minimal_form_data():
    '''
    Define a minimal fields for submit a biblioref form
    '''

    form_data = { 
        'status': '0',
        
        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0', 
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-keyword-content_type-object_id-TOTAL_FORMS': '0', 
        'main-keyword-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',
    }

    return form_data

def complete_form_data():
    '''
    Define missing fields for a valid submission of biblioref object
    '''

    missing_fields = {
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


def create_test_objects():
    '''
    Create biblioref objects for tests
    '''
    BiblioRef.objects.create(status=0, metadata='{title: "Referência de teste 1 (BR1.1)"}', 
                            created_by_id=1, cooperative_center_code='BR1.1')
    
    ct_id = ContentType.objects.get_for_model(BiblioRef)
    descriptor = Descriptor.objects.create(object_id=1, content_type=ct_id, text='descritor 1')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=ct_id, thematic_area_id=1)

    BiblioRef.objects.create(status=0, metadata='{title:"Referência de teste 2 (PY3.1)"}', 
                            created_by_id=2, cooperative_center_code='PY3.1')


class BiblioRefTest(BaseTestCase):
    """
    Tests for ref app
    """

    def setUp(self):
        super(BiblioRefTest, self).setUp()

        # create auxiliary models used on tests        
        thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')


    def test_list(self):
        """
        Test list view
        """
        self.login_editor()
        create_test_objects()

        response = self.client.get('/biblioref/')
        self.assertContains(response, "Referência de teste 1 (BR1.1")

        # list only references from user cooperative center (BR1.1)
        self.assertNotContains(response, "Referência de teste 2 (PY3.1)")        

'''
    def test_add(self):
        """
        Tests create media
        """
        self.login_editor()        

        # invalid submission with missing required fields
        form_data = minimal_form_data()
        response = self.client.post('/multimedia/new', form_data )
        
        self.assertContains(response,'Por favor verifique os campos obrigatórios')
        self.assertContains(response,'Você precisa inserir pelo menos um descritor de assunto')
        self.assertContains(response,'Você precisa selecionar pelo menos uma área temática')

        # complete form_data with required fields and re-submit form
        form_data = complete_form_data()

        # test valid submission
        # after submit a valid content the view will redirect to /multimedia and list the objects
        # follow=True will allow check if the new data is on the list
        response = self.client.post('/multimedia/new', form_data, follow=True)
        self.assertRedirects(response, '/multimedia/')
        self.assertContains(response, "Foto 1")

        # check if is set cooperative center code of user (editor = BR1.1)
        self.assertEquals(Media.objects.all()[0].cooperative_center_code, "BR1.1")
        
    def test_edit(self):
        """
        Tests edit media
        """
        self.login_editor()
        create_media_object()

        media_test = Media.objects.all()[0]
        url = '/multimedia/edit/{0}'.format(media_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, media_test.title)

        # Test changes values and submit
        form_data = complete_form_data()
        form_data['status'] = '1'

        response = self.client.post(url, form_data)
        # check for validation of descriptor and thematic area for status = Admitted
        self.assertContains(response, "é necessário ter pelo menos um descritor")

        # check for normal edition
        form_data['status'] = '0'
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/multimedia/')
        self.assertContains(response, "Foto 1")


    def test_delete(self):
        """
        Tests delete media 
        """
        self.login_editor()
        create_media_object()

        response = self.client.get('/multimedia/delete/1')
        self.assertContains(response, "Você tem certeza?")

        response = self.client.post('/multimedia/delete/1')

        self.assertTrue(Media.objects.filter(id=1).count() == 0)
        self.assertTrue(Descriptor.objects.filter(object_id=1).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=1).count() == 0)

        self.assertRedirects(response, '/multimedia/')

'''