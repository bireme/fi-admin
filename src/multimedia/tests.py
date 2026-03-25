#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from model_bakery import baker

from .models import *
from main.models import Descriptor, ResourceThematic, ThematicArea
from utils.tests import BaseTestCase


def minimal_form_data():
    '''
    Define a minimal fields for submit a media form
    '''

    form_data = {
        'status': '0',
        'title': 'Foto 1',
        'description': 'Foto 1',
        'description_translations': 'null',
        'media_type' : '1',

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-keyword-content_type-object_id-TOTAL_FORMS': '0',
        'main-keyword-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',

        'attachments-attachment-content_type-object_id-TOTAL_FORMS': '0',
        'attachments-attachment-content_type-object_id-INITIAL_FORMS': '0',
    }

    return form_data


def complete_form_data():
    '''
    Define missing fields for a valid submission of media object
    '''

    missing_fields = {
        'link'  : 'http://www.youtube.com',
        'publication_date' : '01/12/2015',

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


def create_media_object(user):
    '''
    Create media object for tests
    '''
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

    # Create a Media object and test that is present on list
    media1 = Media.objects.create(status=0,title='Midia de teste (BR1.1)',
                            media_type_id=1, link='http://bvsalud.org', created_by=user,
                            cooperative_center_code='BR1.1')

    media_ct = ContentType.objects.get_for_model(media1)
    descriptor = Descriptor.objects.create(object_id=1, content_type=media_ct, text='malaria')
    thematic = ResourceThematic.objects.create(object_id=1, content_type=media_ct, thematic_area_id=1)

    media2 = Media.objects.create(status=0,title='Media de prueba (PY3.1)',
                            media_type_id=1, link='http://bvsalud.org', created_by=user2,
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
        user = self.login_editor()
        create_media_object(user)

        response = self.client.get('/multimedia/')
        self.assertContains(response, "Midia de teste (BR1.1")

        # list only medias from user cooperative center (BR1.1)
        self.assertNotContains(response, "Media de prueba (PY3.1)")


    def test_add_media(self):
        """
        Tests create media
        """
        self.login_editor()

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
        user = self.login_editor()
        create_media_object(user)

        media_test = Media.objects.all()[0]
        url = '/multimedia/edit/{0}'.format(media_test.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, media_test.title)

        # Test changes values and submit
        # use minimal_form_data (no descriptors/thematics) to trigger validation error for status=Admitted
        form_data = minimal_form_data()
        form_data['status'] = '1'
        form_data['link'] = 'http://www.youtube.com'
        form_data['publication_date'] = '01/12/2015'

        response = self.client.post(url, form_data)
        # check for validation of descriptor and thematic area for status = Admitted
        self.assertContains(response, "é necessário ter pelo menos um descritor")

        # check for normal edition
        form_data = complete_form_data()
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/multimedia/')
        self.assertContains(response, "Foto 1")


    def test_delete_media(self):
        """
        Tests delete media
        """
        user = self.login_editor()
        create_media_object(user)

        response = self.client.get('/multimedia/delete/1')
        self.assertContains(response, "Você tem certeza que deseja apagar?")

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
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')
        user3 = User.objects.create_user('user3', 'user3@test.com', 'user3')

        # Create a media collection object and test that is present on list
        MediaCollection.objects.create(name='Coleção 1',
                                        description='Coleção de teste 1',
                                        created_by=user, cooperative_center_code='BR1.1')

        MediaCollection.objects.create(name='Coleção 2',
                                        description='Coleção de teste 2',
                                        created_by=user2, cooperative_center_code='BR1.1')

        MediaCollection.objects.create(name='Coleção 3',
                                        description='Coleção de teste 3',
                                        created_by=user3, cooperative_center_code='PY3.8')


        response = self.client.get('/multimedia/collections')
        # check if only one collection is returned (restrict by user)
        self.assertContains(response, "Coleção 1")
        self.assertEquals(response.context['object_list'].count(), 3)

        # check if return only colections from cooperative center BR1.1
        response = self.client.get('/multimedia/collections/?filter_created_by_cc=BR1.1')
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


class MultimediaListViewTest(BaseTestCase):
    """
    Tests for multimedia list view filtering, search, ordering, and context data
    """

    def setUp(self):
        super(MultimediaListViewTest, self).setUp()
        self.media_type = MediaType.objects.create(acronym='video', name='Video')
        self.thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    # -- Owner filtering --

    def test_media_list_default_filters_by_user(self):
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        Media.objects.create(
            status=0, title='Media do editor', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Media do user2', media_type=self.media_type,
            link='http://example.com', created_by=user2, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Media do editor')
        self.assertNotContains(response, 'Media do user2')

    def test_media_list_filter_owner_all(self):
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        Media.objects.create(
            status=0, title='Media do editor', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Media do user2', media_type=self.media_type,
            link='http://example.com', created_by=user2, cooperative_center_code='PY3.1',
        )

        response = self.client.get('/multimedia/', {'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 2)

    # -- Status filtering --

    def test_media_list_filter_by_status(self):
        user = self.login_editor()

        Media.objects.create(
            status=0, title='Pending media', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=1, title='Admitted media', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/', {'filter_status': '1', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Admitted media')
        self.assertNotContains(response, 'Pending media')

    # -- Thematic area filtering --

    def test_media_list_filter_by_thematic_area(self):
        user = self.login_editor()

        media1 = Media.objects.create(
            status=0, title='Media with thematic', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        media2 = Media.objects.create(
            status=0, title='Media without thematic', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )

        media1_ct = ContentType.objects.get_for_model(media1)
        ResourceThematic.objects.create(
            object_id=media1.id, content_type=media1_ct,
            thematic_area=self.thematic_area,
        )

        response = self.client.get('/multimedia/', {
            'filter_thematic': str(self.thematic_area.id),
            'filter_owner': '*',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Media with thematic')
        self.assertNotContains(response, 'Media without thematic')

    # -- Created by user filtering --

    def test_media_list_filter_by_created_by_user(self):
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        Media.objects.create(
            status=0, title='Media do editor', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Media do user2', media_type=self.media_type,
            link='http://example.com', created_by=user2, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/', {
            'filter_created_by_user': str(user2.id),
            'filter_owner': '*',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Media do user2')
        self.assertNotContains(response, 'Media do editor')

    # -- Cooperative center filtering --

    def test_media_list_filter_by_cc(self):
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        Media.objects.create(
            status=0, title='Media BR', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Media PY', media_type=self.media_type,
            link='http://example.com', created_by=user2, cooperative_center_code='PY3.1',
        )

        response = self.client.get('/multimedia/', {
            'filter_created_by_cc': 'BR1.1',
            'filter_owner': '*',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Media BR')
        self.assertNotContains(response, 'Media PY')

    # -- Search --

    def test_media_list_search_by_title(self):
        user = self.login_editor()

        Media.objects.create(
            status=0, title='Malaria video', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Dengue video', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/', {'s': 'Malaria', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Malaria video')
        self.assertNotContains(response, 'Dengue video')

    def test_media_list_search_by_field(self):
        user = self.login_editor()

        Media.objects.create(
            status=0, title='Unique title here', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Another media', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/', {'s': 'title:Unique', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Unique title here')
        self.assertNotContains(response, 'Another media')

    # -- Ordering --

    def test_media_list_ordering(self):
        user = self.login_editor()

        Media.objects.create(
            status=0, title='Alpha media', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )
        Media.objects.create(
            status=0, title='Zeta media', media_type=self.media_type,
            link='http://example.com', created_by=user, cooperative_center_code='BR1.1',
        )

        response = self.client.get('/multimedia/', {
            'order': '-', 'orderby': 'title', 'filter_owner': '*',
        })
        self.assertEqual(response.status_code, 200)
        titles = list(response.context['object_list'].values_list('title', flat=True))
        self.assertEqual(titles, ['Zeta media', 'Alpha media'])

    # -- Context data --

    def test_media_list_context_data(self):
        self.login_editor()

        response = self.client.get('/multimedia/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('actions', response.context)
        self.assertIn('cc_filter_list', response.context)
        self.assertIn('thematic_list', response.context)
        self.assertIn('collection_list', response.context)
        self.assertIn('show_advaced_filters', response.context)

    # -- Access control --

    def test_media_list_unauthenticated_redirects(self):
        response = self.client.get('/multimedia/')
        self.assertEqual(response.status_code, 302)

    # -- MediaType list view --

    def test_media_type_list_requires_superuser(self):
        self.login_editor()
        response = self.client.get('/multimedia/media-types/')
        self.assertEqual(response.status_code, 403)

    def test_media_type_list_superuser_access(self):
        self.login_admin()
        MediaType.objects.create(acronym='foto', name='Foto')

        response = self.client.get('/multimedia/media-types/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Foto')

    def test_media_type_list_no_user_restriction(self):
        admin = self.login_admin()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        MediaType.objects.create(acronym='foto', name='Foto', created_by=admin)
        MediaType.objects.create(acronym='audio', name='Audio', created_by=user2)

        response = self.client.get('/multimedia/media-types/')
        self.assertEqual(response.status_code, 200)
        # restrict_by_user=False, so all types should appear (+ the one from setUp)
        self.assertTrue(response.context['object_list'].count() >= 2)

    # -- MediaCollection list view --

    def test_media_collection_list_filter_by_cc(self):
        self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        MediaCollection.objects.create(name='Col BR', description='test', created_by=user2, cooperative_center_code='BR1.1')
        MediaCollection.objects.create(name='Col PY', description='test', created_by=user2, cooperative_center_code='PY3.1')

        response = self.client.get('/multimedia/collections/', {'filter_created_by_cc': 'BR1.1'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Col BR')
        self.assertNotContains(response, 'Col PY')

    def test_media_collection_list_search(self):
        self.login_editor()

        MediaCollection.objects.create(name='Fotos antigas', description='test', cooperative_center_code='BR1.1')
        MediaCollection.objects.create(name='Videos recentes', description='test', cooperative_center_code='BR1.1')

        response = self.client.get('/multimedia/collections/', {'s': 'Fotos'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), 1)
        self.assertContains(response, 'Fotos antigas')
        self.assertNotContains(response, 'Videos recentes')

    def test_media_collection_list_no_user_restriction(self):
        user = self.login_editor()
        user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

        MediaCollection.objects.create(name='Col editor', description='test', created_by=user, cooperative_center_code='BR1.1')
        MediaCollection.objects.create(name='Col user2', description='test', created_by=user2, cooperative_center_code='PY3.1')

        response = self.client.get('/multimedia/collections/')
        self.assertEqual(response.status_code, 200)
        # restrict_by_user=False, so all collections should appear
        self.assertEqual(response.context['object_list'].count(), 2)

    # -- Advanced filters flag --

    def test_show_advanced_filters(self):
        self.login_editor()

        response = self.client.get('/multimedia/', {'apply_filters': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_advaced_filters'])


class MultimediaSearchTest(BaseTestCase):
    def test_search_id(self):
        self.login_editor()

        mt = baker.make("MediaType")
        baker.make("Media", media_type=mt, id=1)
        baker.make("Media", media_type=mt, id=2)
        baker.make("Media", media_type=mt, id=3)

        resp1 = self.client.get("/multimedia/", {"s": "id:1", "filter_owner": "*"})
        self.assertEqual(200, resp1.status_code)
        self.assertContains(resp1, '<a href="/multimedia/edit/1">1</a')
        self.assertNotContains(resp1, '<a href="/multimedia/edit/2">2</a')
        self.assertNotContains(resp1, '<a href="/multimedia/edit/3">3</a')

        resp2 = self.client.get("/multimedia/", {"s": "id:2", "filter_owner": "*"})
        self.assertEqual(200, resp2.status_code)
        self.assertContains(resp2, '<a href="/multimedia/edit/2">2</a')
        self.assertNotContains(resp2, '<a href="/multimedia/edit/1">1</a')
        self.assertNotContains(resp2, '<a href="/multimedia/edit/3">3</a')

        resp3 = self.client.get("/multimedia/", {"s": "id:3", "filter_owner": "*"})
        self.assertEqual(200, resp3.status_code)
        self.assertContains(resp3, '<a href="/multimedia/edit/3">3</a')
        self.assertNotContains(resp3, '<a href="/multimedia/edit/1">1</a')
        self.assertNotContains(resp3, '<a href="/multimedia/edit/2">2</a')
