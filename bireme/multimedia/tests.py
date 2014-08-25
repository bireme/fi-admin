# coding: utf-8
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from main.models import ThematicArea, Descriptor, ResourceThematic

from models import *

def minimal_form_data():
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
    missing_fields = {
        'url'  : 'http://www.youtube.com',

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
    
    # Create a Media object and test that is present on list
    media = Media.objects.create(status=0,title='Midia de teste', 
                            media_type_id=1, url='http://bvsalud.org', created_by_id=1)
    
    media_ct = ContentType.objects.get_for_model(media)
    descriptor = Descriptor.objects.create(object_id=1, content_type=media_ct, text='malaria')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=media_ct, thematic_area_id=1)

@override_settings(AUTHENTICATION_BACKENDS=('django.contrib.auth.backends.ModelBackend',))
class MultimediaTest(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

        # Create auxiliary tables 
        media_type = MediaType.objects.create(acronym='video', name='Video')
        thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    def login_editor(self):
        user_editor =  User.objects.create_user('editor', 'user@test.com', 'editor')
        user_editor.profile.data = '''
        {
            "user_role" : "normal",
            "cc" : "BR1.2", 
            "user_id" : 1,
            "service_role": [{"Multimedia" : "edi"}], 
            "user_name" : "Editor",
            "ccs" : ["BR1.2"],
            "networks" : ["NETWORK 1"]
        }
        '''
        user_editor.profile.save()
      
        self.client.login(username='editor', password='editor')

    def login_admin(self):
        # only superuser can edit lists
        user_admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username='admin', password='admin')


    def test_list_media(self):
        """
        Tests list of media pages
        """
        self.login_editor()
        create_media_object()

        response = self.client.get('/multimedia/')
        self.assertContains(response, "Midia de teste")

    def test_add_media(self):
        """
        Tests add new media
        """
        self.login_editor()        

        # Test invalid submission with missing required fields
        form_data = minimal_form_data()
        response = self.client.post('/multimedia/new', form_data )
        
        self.assertContains(response,'Por favor verifique os campos obrigatórios')
        self.assertContains(response,'Você precisa inserir pelo menos um descritor de assunto')
        self.assertContains(response,'Você precisa selecionar pelo menos uma área temática')

        # complete form_data with required fields and re-submit form
        form_data = complete_form_data()

        # Test valid submission
        # After submit a valid content the view will redirect to /multimedia and list the objects
        # follow=True will allow check if the new data is on the list
        response = self.client.post('/multimedia/new', form_data, follow=True)
        self.assertRedirects(response, '/multimedia/')
        self.assertContains(response, "Foto 1")

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

        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/multimedia/')
        self.assertContains(response, "Foto 1")


    def test_delete_media(self):
        """
        Tests delete of media 
        """
        self.login_editor()
        create_media_object()

        response = self.client.get('/multimedia/delete/1')
        self.assertContains(response, "Você tem certeza?")

        response = self.client.post('/multimedia/delete/1')

        self.assertTrue(Media.objects.count() == 0)
        self.assertTrue(Descriptor.objects.filter(object_id=1).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=1).count() == 0)

        self.assertRedirects(response, '/multimedia/')


    def test_list_media_type(self):
        """
        Tests list media type
        """
        self.login_admin()

        response = self.client.get('/multimedia/media-types/')
        self.assertContains(response, "Video")


    def test_add_media(self):
        """
        Tests add new media type
        """
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
        media_collection = MediaCollection.objects.create(name='Coleção 1', 
                                        description='Coleção de teste', created_by_id=1)


        response = self.client.get('/multimedia/collections')
        self.assertContains(response, "Coleção 1")


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

