# coding: utf-8

from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from main.models import Descriptor, ResourceThematic, ThematicArea

from utils.tests import BaseTestCase
from models import *

def minimal_form_data():
    '''
    Define a minimal fields for submit a media form
    '''

    form_data = { 
        'status': '0',
        'title': 'Foto 1',
        'description': 'Foto 1',
        'media_type' : '1',
        
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
    Define missing fields for a valid submission of media object
    '''

    missing_fields = {
        'link'  : 'http://www.youtube.com',

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


def create_media_object():
    '''
    Create media object for tests
    '''
    
    # Create a Media object and test that is present on list
    media1 = Media.objects.create(status=0,title='Midia de teste (BR1.1)', 
                            media_type_id=1, link='http://bvsalud.org', created_by_id=1,
                            cooperative_center_code='BR1.1')
    
    media_ct = ContentType.objects.get_for_model(media1)
    descriptor = Descriptor.objects.create(object_id=1, content_type=media_ct, text='malaria')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=media_ct, thematic_area_id=1)

    media2 = Media.objects.create(status=0,title='Media de prueba (PY3.1)', 
                            media_type_id=1, link='http://bvsalud.org', created_by_id=2,
                            cooperative_center_code='PY3.1')


class MultimediaTest(BaseTestCase):
    """
    Tests for multimedia app
    """

    def setUp(self):
        super(MultimediaTest, self).setUp()

        # create auxiliary models used on tests
        media_type = MediaType.objects.create(acronym='video', name='Video')
        thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')


    def test_list_media(self):
        """
        Test list media
        """
        self.login_editor()
        create_media_object()

        response = self.client.get('/multimedia/')
        self.assertContains(response, "Midia de teste (BR1.1")

        # list only medias from user cooperative center (BR1.1)
        self.assertNotContains(response, "Media de prueba (PY3.1)")        


    def test_add_media(self):
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
        
    def test_edit_media(self):
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


    def test_delete_media(self):
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


    def test_list_media_type(self):
        """
        Tests list media type
        """

        # check if documentalist has access to list media-types
        self.login_documentalist()
        response = self.client.get('/multimedia/media-types/' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        response = self.client.get('/multimedia/media-types/')
        self.assertContains(response, "Video")


    def test_add_media_type(self):
        """
        Tests create media type
        """

        # check if documentalist has access to create new media-types
        self.login_documentalist()
        response = self.client.get('/multimedia/media-type/new' )

        # 403 = unauthorized
        self.assertEqual(response.status_code, 403)

        self.client.logout()
        self.login_admin()

        form_data = { 
            'status': '0',
            'acronym': 'foto',
            'name': 'Foto',
            'language' : 'pt-br',
            'mediatypelocal_set-TOTAL_FORMS': '0', 
            'mediatypelocal_set-INITIAL_FORMS': '0',
        }

        response = self.client.post('/multimedia/media-type/new', form_data, follow=True )
       
        self.assertRedirects(response, '/multimedia/media-types')
        self.assertContains(response, "Foto")


    def test_list_media_collection(self):
        """
        Tests list of media collection
        """
        self.login_editor()

        # Create a media collection object and test that is present on list
        MediaCollection.objects.create(name='Coleção 1', 
                                        description='Coleção de teste 1', 
                                        created_by_id=1, cooperative_center_code='BR1.1')

        MediaCollection.objects.create(name='Coleção 2', 
                                        description='Coleção de teste 2', 
                                        created_by_id=2, cooperative_center_code='BR1.1')

        MediaCollection.objects.create(name='Coleção 3', 
                                        description='Coleção de teste 3', 
                                        created_by_id=3, cooperative_center_code='PY3.8')


        response = self.client.get('/multimedia/collections')
        # check if only one collection is returned (restrict by user)
        self.assertContains(response, "Coleção 1")
        self.assertEquals(response.context['object_list'].count(), 1)
        
        # check if return only colections from cooperative center BR1.1
        response = self.client.get('/multimedia/collections/?filter_owner=*')
        self.assertEquals(response.context['object_list'].count(), 2)


    def test_add_media_collection(self):
        """
        Tests add media collection
        """
        self.login_editor()

        form_data = { 
            'name': 'Coleção nova',
            'description': 'Coleção de teste',
            'language': 'pt-br',
            'mediacollectionlocal_set-TOTAL_FORMS': '0', 
            'mediacollectionlocal_set-INITIAL_FORMS': '0',            
        }

        response = self.client.post('/multimedia/collection/new', form_data, follow=True )
       
        self.assertRedirects(response, '/multimedia/collections')
        self.assertContains(response, "Coleção nova")

