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
    Define minimal fields for submitting an OER form
    '''
    form_data = {
        'status': '-1',
        'title': 'Recurso educacional de teste',
        'CVSP_resource': True,

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',

        'attachments-attachment-content_type-object_id-TOTAL_FORMS': '0',
        'attachments-attachment-content_type-object_id-INITIAL_FORMS': '0',

        'oerurl_set-TOTAL_FORMS': '0',
        'oerurl_set-INITIAL_FORMS': '0',

        'related-TOTAL_FORMS': '0',
        'related-INITIAL_FORMS': '0',
    }

    return form_data


def complete_form_data(thematic_area_id, oer_type_id, language_id, license_id,
                       learning_context_id):
    '''
    Define all required fields for a valid Published submission of an OER
    '''
    missing_fields = {
        'status': '1',
        'learning_objectives': 'Objetivo de aprendizagem de teste',
        'description': 'Descrição de teste',
        'creator': '[{"name": "Autor Teste"}]',
        'type': str(oer_type_id),
        'language': str(language_id),
        'license': str(license_id),
        'learning_context': str(learning_context_id),

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '1',
        'main-descriptor-content_type-object_id-0-id': '',
        'main-descriptor-content_type-object_id-0-text': 'malaria',
        'main-descriptor-content_type-object_id-0-code': '^d8462',
        'main-descriptor-content_type-object_id-0-status': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '1',
        'main-resourcethematic-content_type-object_id-0-thematic_area': str(thematic_area_id),
        'main-resourcethematic-content_type-object_id-0-status': '0',
    }

    form_data = minimal_form_data()
    form_data.update(missing_fields)

    return form_data


def create_oer_object(user, oer_type, language, license, learning_context, thematic_area):
    '''
    Create OER objects for tests
    '''
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

    oer1 = OER.objects.create(
        status=-1, title='Recurso educacional de teste (BR1.1)',
        type=oer_type, language=language, license=license,
        learning_context=learning_context,
        created_by=user, cooperative_center_code='BR1.1'
    )

    oer_ct = ContentType.objects.get_for_model(oer1)
    Descriptor.objects.create(object_id=oer1.id, content_type=oer_ct, text='malaria')
    ResourceThematic.objects.create(object_id=oer1.id, content_type=oer_ct,
                                    thematic_area=thematic_area)

    oer2 = OER.objects.create(
        status=-1, title='Recurso educativo de prueba (PY3.1)',
        type=oer_type, language=language, license=license,
        learning_context=learning_context,
        created_by=user2, cooperative_center_code='PY3.1'
    )

    return oer1, oer2


class OERTest(BaseTestCase):
    """
    Tests for oer app
    """

    def setUp(self):
        super(OERTest, self).setUp()

        # create auxiliary models used on tests
        self.oer_type = Type.objects.create(name='Curso', language='pt-br')
        self.language = SourceLanguage.objects.create(acronym='pt', name='Portugues',
                                                      language='pt-br')
        self.license = License.objects.create(name='CC BY', language='pt-br')
        self.learning_context = LearningContext.objects.create(name='Ensino superior',
                                                               language='pt-br')
        self.thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    def test_list_oer(self):
        """
        Test list OER
        """
        user = self.login_admin()
        create_oer_object(user, self.oer_type, self.language, self.license,
                          self.learning_context, self.thematic_area)

        response = self.client.get('/oer/')
        self.assertContains(response, "Recurso educacional de teste (BR1.1)")

        # list only OERs from user (default filter_owner='user')
        self.assertNotContains(response, "Recurso educativo de prueba (PY3.1)")

    def test_add_oer(self):
        """
        Tests create OER
        """
        self.login_admin()

        form_data = complete_form_data(self.thematic_area.id, self.oer_type.id,
                                       self.language.id, self.license.id,
                                       self.learning_context.id)

        response = self.client.post('/oer/new', form_data, follow=True)
        self.assertRedirects(response, '/oer/')
        self.assertContains(response, "Recurso educacional de teste")

        # check if cooperative center code is set from user profile (admin = BR1.1)
        self.assertEqual(OER.objects.all()[0].cooperative_center_code, "BR1.1")

    def test_edit_oer(self):
        """
        Tests edit OER
        """
        user = self.login_admin()
        oer1, oer2 = create_oer_object(user, self.oer_type, self.language,
                                        self.license, self.learning_context,
                                        self.thematic_area)

        url = '/oer/edit/{0}'.format(oer1.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, oer1.title)

        # Test changes values and submit
        form_data = complete_form_data(self.thematic_area.id, self.oer_type.id,
                                       self.language.id, self.license.id,
                                       self.learning_context.id)
        form_data['title'] = 'Recurso editado'
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/oer/')
        self.assertContains(response, "Recurso editado")

    def test_delete_oer(self):
        """
        Tests delete OER
        """
        user = self.login_admin()
        oer1, oer2 = create_oer_object(user, self.oer_type, self.language,
                                        self.license, self.learning_context,
                                        self.thematic_area)

        response = self.client.get('/oer/delete/{0}'.format(oer1.id))
        self.assertContains(response, "Você tem certeza que deseja apagar?")

        response = self.client.post('/oer/delete/{0}'.format(oer1.id))

        self.assertTrue(OER.objects.filter(id=oer1.id).count() == 0)

        oer_ct = ContentType.objects.get_for_model(OER)
        self.assertTrue(Descriptor.objects.filter(object_id=oer1.id, content_type=oer_ct).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=oer1.id, content_type=oer_ct).count() == 0)

        self.assertRedirects(response, '/oer/')


class OERListViewTest(BaseTestCase):
    """
    Tests for OERGenericListView filtering, search, ordering and context
    """

    def setUp(self):
        super(OERListViewTest, self).setUp()

        self.oer_type = Type.objects.create(name='Curso', language='pt-br')
        self.language = SourceLanguage.objects.create(acronym='pt', name='Portugues',
                                                      language='pt-br')
        self.license = License.objects.create(name='CC BY', language='pt-br')
        self.learning_context = LearningContext.objects.create(name='Ensino superior',
                                                               language='pt-br')
        self.thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    def _create_oer(self, user, title='Test OER', status=-1, cc='BR1.1', cvsp_node=''):
        """Helper to create a single OER with given attributes"""
        return OER.objects.create(
            status=status, title=title,
            type=self.oer_type, language=self.language,
            license=self.license, learning_context=self.learning_context,
            created_by=user, cooperative_center_code=cc, cvsp_node=cvsp_node
        )

    # --- 1. Owner filtering ---

    def test_list_default_filters_by_user(self):
        """Default list filters by current user (filter_owner='user')"""
        admin = self.login_admin()
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        self._create_oer(admin, title='Admin OER')
        self._create_oer(other_user, title='Other OER')

        response = self.client.get('/oer/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin OER')
        self.assertNotContains(response, 'Other OER')

    def test_list_filter_owner_center(self):
        """filter_owner=center filters by cooperative center code"""
        admin = self.login_admin()
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        self._create_oer(admin, title='BR1.1 OER', cc='BR1.1')
        self._create_oer(other_user, title='PY3.1 OER', cc='PY3.1')

        response = self.client.get('/oer/', {'filter_owner': 'center'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BR1.1 OER')
        self.assertNotContains(response, 'PY3.1 OER')

    def test_list_filter_owner_all(self):
        """filter_owner=* shows all records regardless of creator"""
        admin = self.login_admin()
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        self._create_oer(admin, title='Admin OER')
        self._create_oer(other_user, title='Other OER')

        response = self.client.get('/oer/', {'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin OER')
        self.assertContains(response, 'Other OER')

    # --- 2. Status filtering ---

    def test_list_filter_by_status(self):
        """filter_status filters OERs by status field"""
        user = self.login_admin()

        self._create_oer(user, title='Draft OER', status=-1)
        self._create_oer(user, title='Published OER', status=1)

        response = self.client.get('/oer/', {'filter_status': '1', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published OER')
        self.assertNotContains(response, 'Draft OER')

    # --- 3. Country/CVSP node filtering ---

    def test_list_filter_by_country(self):
        """filter_country filters OERs by cvsp_node"""
        user = self.login_admin()

        self._create_oer(user, title='BR OER', cvsp_node='BR')
        self._create_oer(user, title='PY OER', cvsp_node='PY')

        response = self.client.get('/oer/', {
            'filter_country': 'BR', 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BR OER')
        self.assertNotContains(response, 'PY OER')

    # --- 4. Search functionality ---

    def test_list_search_by_title(self):
        """Search matches title via icontains"""
        user = self.login_admin()

        self._create_oer(user, title='Unique Educational Resource')
        self._create_oer(user, title='Other Record')

        response = self.client.get('/oer/', {'s': 'Unique Educational', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Educational Resource')
        self.assertNotContains(response, 'Other Record')

    def test_list_search_by_field_prefix(self):
        """Search with field:value syntax uses icontains on specified field"""
        user = self.login_admin()

        self._create_oer(user, title='Target Title')
        self._create_oer(user, title='Other Title')

        response = self.client.get('/oer/', {'s': 'title:Target', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Target Title')
        self.assertNotContains(response, 'Other Title')

    def test_list_empty_search_returns_all(self):
        """Empty search string returns all records"""
        user = self.login_admin()

        self._create_oer(user, title='OER One')
        self._create_oer(user, title='OER Two')

        response = self.client.get('/oer/', {'s': '', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OER One')
        self.assertContains(response, 'OER Two')

    # --- 5. Ordering ---

    def test_list_ordering(self):
        """order=- with orderby applies descending sort"""
        user = self.login_admin()

        self._create_oer(user, title='AAA OER')
        self._create_oer(user, title='ZZZ OER')

        response = self.client.get('/oer/', {
            'order': '-', 'orderby': 'title', 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        pos_zzz = content.find('ZZZ OER')
        pos_aaa = content.find('AAA OER')
        self.assertGreater(pos_zzz, -1)
        self.assertGreater(pos_aaa, -1)
        self.assertLess(pos_zzz, pos_aaa)

    # --- 6. Context data ---

    def test_list_context_data(self):
        """Context contains expected keys"""
        self.login_admin()

        response = self.client.get('/oer/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('actions', response.context)
        self.assertIn('user_role', response.context)
        self.assertIn('cvsp_node_list', response.context)
        self.assertIn('show_advaced_filters', response.context)

    # --- 7. Access control ---

    def test_list_unauthenticated_redirects(self):
        """Unauthenticated access redirects to login"""
        response = self.client.get('/oer/')
        self.assertEqual(response.status_code, 302)

    # --- 8. Advanced filters flag ---

    def test_show_advanced_filters(self):
        """apply_filters parameter sets show_advaced_filters in context"""
        self.login_admin()

        response = self.client.get('/oer/', {'apply_filters': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_advaced_filters'])


class OERSearchTest(BaseTestCase):
    def test_search_id(self):
        self.login_admin()

        baker.make("oer.OER", id=1)
        baker.make("oer.OER", id=2)
        baker.make("oer.OER", id=3)

        resp1 = self.client.get("/oer/", {"s": "id:1", "filter_owner": "*"})
        self.assertEqual(200, resp1.status_code)
        self.assertContains(resp1, '<a href="/oer/edit/1">1</a')
        self.assertNotContains(resp1, '<a href="/oer/edit/2">2</a')
        self.assertNotContains(resp1, '<a href="/oer/edit/3">3</a')

        resp2 = self.client.get("/oer/", {"s": "id:2", "filter_owner": "*"})
        self.assertEqual(200, resp2.status_code)
        self.assertContains(resp2, '<a href="/oer/edit/2">2</a')
        self.assertNotContains(resp2, '<a href="/oer/edit/1">1</a')
        self.assertNotContains(resp2, '<a href="/oer/edit/3">3</a')

        resp3 = self.client.get("/oer/", {"s": "id:3", "filter_owner": "*"})
        self.assertEqual(200, resp3.status_code)
        self.assertContains(resp3, '<a href="/oer/edit/3">3</a')
        self.assertNotContains(resp3, '<a href="/oer/edit/1">1</a')
        self.assertNotContains(resp3, '<a href="/oer/edit/2">2</a')
