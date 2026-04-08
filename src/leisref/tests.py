#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from model_bakery import baker

from .models import *
from main.models import Descriptor, ResourceThematic, ThematicArea
from classification.models import Collection, Relationship
from utils.tests import BaseTestCase


def minimal_form_data(scope_region_id, act_type_id):
    '''
    Define minimal fields for submitting an Act form
    '''
    form_data = {
        'status': '-1',
        'scope_region': str(scope_region_id),
        'act_type': str(act_type_id),
        'title': 'Ato de teste',
        'official_ementa_translations': 'null',
        'unofficial_ementa_translations': 'null',

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
        'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',

        'attachments-attachment-content_type-object_id-TOTAL_FORMS': '0',
        'attachments-attachment-content_type-object_id-INITIAL_FORMS': '0',

        'acturl_set-TOTAL_FORMS': '0',
        'acturl_set-INITIAL_FORMS': '0',

        'related-TOTAL_FORMS': '0',
        'related-INITIAL_FORMS': '0',
    }

    return form_data


def complete_form_data(scope_region_id, act_type_id, thematic_area_id):
    '''
    Define all required fields for a valid Published submission of an Act
    '''
    missing_fields = {
        'issue_date': '01/01/2020',
        'publication_date': '15/01/2020',

        'main-descriptor-content_type-object_id-TOTAL_FORMS': '1',
        'main-descriptor-content_type-object_id-0-id': '',
        'main-descriptor-content_type-object_id-0-text': 'malaria',
        'main-descriptor-content_type-object_id-0-code': '^d8462',
        'main-descriptor-content_type-object_id-0-status': '0',

        'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '1',
        'main-resourcethematic-content_type-object_id-0-thematic_area': str(thematic_area_id),
        'main-resourcethematic-content_type-object_id-0-status': '0',
    }

    form_data = minimal_form_data(scope_region_id, act_type_id)
    form_data.update(missing_fields)

    return form_data


def create_act_object(user, scope_region, act_type, thematic_area):
    '''
    Create Act objects for tests
    '''
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

    act1 = Act.objects.create(
        status=-1, title='Ato de teste (BR1.1)',
        scope_region=scope_region, act_type=act_type,
        created_by=user, cooperative_center_code='BR1.1'
    )

    act_ct = ContentType.objects.get_for_model(act1)
    Descriptor.objects.create(object_id=act1.id, content_type=act_ct, text='malaria')
    ResourceThematic.objects.create(object_id=act1.id, content_type=act_ct,
                                    thematic_area=thematic_area)

    act2 = Act.objects.create(
        status=-1, title='Ato de prueba (PY3.1)',
        scope_region=scope_region, act_type=act_type,
        created_by=user2, cooperative_center_code='PY3.1'
    )

    return act1, act2


class LeisRefTest(BaseTestCase):
    """
    Tests for leisref app
    """

    def setUp(self):
        super(LeisRefTest, self).setUp()

        # create auxiliary models used on tests
        self.scope_region = ActCountryRegion.objects.create(name='Brasil', language='pt-br')
        self.act_type = ActType.objects.create(name='Lei', language='pt-br')
        self.act_type.scope_region.add(self.scope_region)
        self.thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    def test_list_act(self):
        """
        Test list acts
        """
        user = self.login_admin()
        create_act_object(user, self.scope_region, self.act_type, self.thematic_area)

        response = self.client.get('/legislation/')
        self.assertContains(response, "Ato de teste (BR1.1)")

        # list only acts from user cooperative center (BR1.1)
        self.assertNotContains(response, "Ato de prueba (PY3.1)")

    def test_add_act(self):
        """
        Tests create act
        """
        self.login_admin()

        form_data = complete_form_data(self.scope_region.id, self.act_type.id,
                                       self.thematic_area.id)

        response = self.client.post('/legislation/new', form_data, follow=True)
        self.assertRedirects(response, '/legislation/')
        self.assertContains(response, "Ato de teste")

        # check if cooperative center code is set from user profile (admin = BR1.1)
        self.assertEqual(Act.objects.all()[0].cooperative_center_code, "BR1.1")

    def test_edit_act(self):
        """
        Tests edit act
        """
        user = self.login_admin()
        act1, act2 = create_act_object(user, self.scope_region, self.act_type,
                                        self.thematic_area)

        url = '/legislation/edit/{0}'.format(act1.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, act1.title)

        # Test changes values and submit
        form_data = complete_form_data(self.scope_region.id, self.act_type.id,
                                       self.thematic_area.id)
        form_data['title'] = 'Ato editado'
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/legislation/')
        self.assertContains(response, "Ato editado")

    def test_delete_act(self):
        """
        Tests delete act
        """
        user = self.login_admin()
        act1, act2 = create_act_object(user, self.scope_region, self.act_type,
                                        self.thematic_area)

        response = self.client.get('/legislation/delete/{0}'.format(act1.id))
        self.assertContains(response, "Você tem certeza que deseja apagar?")

        response = self.client.post('/legislation/delete/{0}'.format(act1.id))

        self.assertTrue(Act.objects.filter(id=act1.id).count() == 0)

        act_ct = ContentType.objects.get_for_model(Act)
        self.assertTrue(Descriptor.objects.filter(object_id=act1.id, content_type=act_ct).count() == 0)
        self.assertTrue(ResourceThematic.objects.filter(object_id=act1.id, content_type=act_ct).count() == 0)

        self.assertRedirects(response, '/legislation/')

    def test_list_act_type(self):
        """
        Tests list act type (auxiliary model)
        """
        self.login_admin()

        response = self.client.get('/legislation/aux-act-type/',
                                   {'s': 'name:Lei', 'filter_owner': '*'})
        self.assertContains(response, "Lei")

    def test_add_act_type(self):
        """
        Tests create act type (auxiliary model)
        """
        self.login_admin()

        form_data = {
            'status': '0',
            'name': 'Decreto',
            'language': 'pt-br',
            'acttypelocal_set-TOTAL_FORMS': '0',
            'acttypelocal_set-INITIAL_FORMS': '0',
        }

        response = self.client.post('/legislation/aux-act-type/new', form_data, follow=True)

        self.assertRedirects(response, '/legislation/aux-act-type')
        # verify the new act type was created in the database
        self.assertTrue(ActType.objects.filter(name='Decreto').exists())


class LeisRefListViewTest(BaseTestCase):
    """
    Tests for LeisRefGenericListView filtering, search, ordering and context
    """

    def setUp(self):
        super(LeisRefListViewTest, self).setUp()

        self.scope_region = ActCountryRegion.objects.create(name='Brasil', language='pt-br')
        self.scope_region2 = ActCountryRegion.objects.create(name='Argentina', language='es')
        self.act_type = ActType.objects.create(name='Lei', language='pt-br')
        self.act_type.scope_region.add(self.scope_region)
        self.act_type2 = ActType.objects.create(name='Decreto', language='pt-br')
        self.act_type2.scope_region.add(self.scope_region)
        self.thematic_area = ThematicArea.objects.create(acronym='LISBR1.1', name='Teste')

    # --- 1. Owner filtering ---

    def test_list_default_filters_by_user(self):
        """Default list filters by current user (restrict_by_user=True)"""
        admin = self.login_admin()
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        Act.objects.create(
            status=-1, title='Admin Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=admin, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Other Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=other_user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Act')
        self.assertNotContains(response, 'Other Act')

    def test_list_filter_owner_all(self):
        """filter_owner=* shows all records regardless of creator"""
        editor = self.login_editor()
        admin_user = User.objects.create_user('other_admin', 'oa@test.com', 'oa')

        Act.objects.create(
            status=-1, title='Editor Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=editor, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Other Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=admin_user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Editor Act')
        self.assertContains(response, 'Other Act')

    # --- 2. Status filtering ---

    def test_list_filter_by_status(self):
        """filter_status filters acts by status field"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Draft Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=1, title='Published Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'filter_status': '1', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Published Act')
        self.assertNotContains(response, 'Draft Act')

    # --- 3. Scope filtering ---

    def test_list_filter_by_scope(self):
        """filter_scope filters acts by scope field"""
        user = self.login_admin()
        act_scope = ActScope.objects.create(name='Federal', language='pt-br')

        Act.objects.create(
            status=-1, title='Federal Act', scope_region=self.scope_region,
            act_type=self.act_type, scope=act_scope, created_by=user,
            cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='No Scope Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'filter_scope': str(act_scope.id), 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Federal Act')
        self.assertNotContains(response, 'No Scope Act')

    # --- 4. Country/Region filtering ---

    def test_list_filter_by_country(self):
        """filter_country filters acts by scope_region"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Brasil Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Argentina Act', scope_region=self.scope_region2,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'filter_country': str(self.scope_region.id), 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brasil Act')
        self.assertNotContains(response, 'Argentina Act')

    # --- 5. Indexed database filtering ---

    def test_list_filter_by_indexed_database(self):
        """filter_indexed_database filters acts by indexed_database M2M"""
        user = self.login_admin()
        db = Database.objects.create(acronym='LILACS', name='LILACS')

        act1 = Act.objects.create(
            status=-1, title='LILACS Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        act1.indexed_database.add(db)

        Act.objects.create(
            status=-1, title='No DB Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'filter_indexed_database': str(db.id), 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LILACS Act')
        self.assertNotContains(response, 'No DB Act')

    # --- 6. Act type filtering ---

    def test_list_filter_by_act_type(self):
        """filter_act_type filters acts by act_type"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Lei Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Decreto Act', scope_region=self.scope_region,
            act_type=self.act_type2, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'filter_act_type': str(self.act_type.id), 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lei Act')
        self.assertNotContains(response, 'Decreto Act')

    # --- 7. Collection filtering ---

    def test_list_filter_by_collection(self):
        """filter_collection filters acts by collection GenericRelation"""
        user = self.login_admin()
        col = Collection.objects.create(name='Test Collection', language='pt-br')

        act1 = Act.objects.create(
            status=-1, title='Collection Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        act_ct = ContentType.objects.get_for_model(act1)
        Relationship.objects.create(
            object_id=act1.id, content_type=act_ct, collection=col
        )

        Act.objects.create(
            status=-1, title='No Collection Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'filter_collection': str(col.id), 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Collection Act')
        self.assertNotContains(response, 'No Collection Act')

    # --- 8. Search functionality ---

    def test_list_search_by_act_number(self):
        """Search by act_number (exact match)"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Act A', act_number='12345',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Act B', act_number='99999',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'s': '12345', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Act A')
        self.assertNotContains(response, 'Act B')

    def test_list_search_by_title(self):
        """Search matches title via icontains"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Unique Legislation Title',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Other Record',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'s': 'Unique Legislation', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Legislation Title')
        self.assertNotContains(response, 'Other Record')

    def test_list_search_by_denomination(self):
        """Search matches denomination via icontains"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Act X', denomination='Special Denomination',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Act Y', denomination='Normal',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'s': 'Special Denomination', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Act X')
        self.assertNotContains(response, 'Act Y')

    def test_list_search_by_field_prefix(self):
        """Search with field:value syntax uses icontains on specified field"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='Target Title',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='Other Title',
            scope_region=self.scope_region, act_type=self.act_type,
            created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {'s': 'title:Target', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Target Title')
        self.assertNotContains(response, 'Other Title')

    # --- 9. Ordering ---

    def test_list_ordering(self):
        """order=- with orderby applies descending sort"""
        user = self.login_admin()

        Act.objects.create(
            status=-1, title='AAA Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )
        Act.objects.create(
            status=-1, title='ZZZ Act', scope_region=self.scope_region,
            act_type=self.act_type, created_by=user, cooperative_center_code='BR1.1'
        )

        response = self.client.get('/legislation/', {
            'order': '-', 'orderby': 'title', 'filter_owner': '*'
        })
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        pos_zzz = content.find('ZZZ Act')
        pos_aaa = content.find('AAA Act')
        self.assertGreater(pos_zzz, -1)
        self.assertGreater(pos_aaa, -1)
        self.assertLess(pos_zzz, pos_aaa)

    # --- 10. Context data ---

    def test_list_context_data(self):
        """Context contains expected keys"""
        self.login_admin()

        response = self.client.get('/legislation/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('actions', response.context)
        self.assertIn('user_role', response.context)
        self.assertIn('scope_list', response.context)
        self.assertIn('scope_region_list', response.context)
        self.assertIn('indexed_database_list', response.context)
        self.assertIn('collection_list', response.context)
        self.assertIn('act_type_list', response.context)

    # --- 11. Access control ---

    def test_list_unauthenticated_redirects(self):
        """Unauthenticated access redirects to login"""
        response = self.client.get('/legislation/')
        self.assertEqual(response.status_code, 302)

    # --- 12. Advanced filters flag ---

    def test_show_advanced_filters(self):
        """apply_filters parameter sets show_advaced_filters in context"""
        self.login_admin()

        response = self.client.get('/legislation/', {'apply_filters': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_advaced_filters'])

    # --- 13. Auxiliary list views ---

    def test_country_region_list_no_user_restriction(self):
        """Country/Region list shows all records (restrict_by_user=False)"""
        self.login_admin()

        response = self.client.get('/legislation/aux-country-region/',
                                   {'s': 'name:Brasil', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brasil')

    def test_act_scope_list(self):
        """Act scope list returns 200"""
        self.login_admin()
        ActScope.objects.create(name='Federal', language='pt-br')

        response = self.client.get('/legislation/aux-act-scope/',
                                   {'s': 'name:Federal', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Federal')

    def test_act_type_list_no_user_restriction(self):
        """Act type list shows all records (restrict_by_user=False)"""
        self.login_admin()

        response = self.client.get('/legislation/aux-act-type/',
                                   {'s': 'name:Lei', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lei')

    def test_act_organ_list(self):
        """Act organ issuer list returns 200"""
        self.login_admin()
        ActOrganIssuer.objects.create(name='Presidencia', language='pt-br')

        response = self.client.get('/legislation/aux-act-organ/',
                                   {'s': 'name:Presidencia', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presidencia')

    def test_act_source_list(self):
        """Act source list returns 200"""
        self.login_admin()
        ActSource.objects.create(name='Diario Oficial', language='pt-br')

        response = self.client.get('/legislation/aux-act-source/',
                                   {'s': 'name:Diario', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diario Oficial')

    def test_act_reltype_list(self):
        """Act relation type list returns 200"""
        self.login_admin()
        ActRelationType.objects.create(name='Revoga', language='pt-br')

        response = self.client.get('/legislation/aux-act-reltype/',
                                   {'s': 'name:Revoga', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Revoga')

    def test_act_state_list(self):
        """Act state list returns 200"""
        self.login_admin()
        ActState.objects.create(name='Sao Paulo', language='pt-br', scope_region=self.scope_region)

        response = self.client.get('/legislation/aux-act-state/',
                                   {'s': 'name:Sao Paulo', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sao Paulo')

    def test_act_city_list(self):
        """Act city list returns 200"""
        self.login_admin()
        ActCity.objects.create(name='Brasilia', language='pt-br', scope_region=self.scope_region)

        response = self.client.get('/legislation/aux-act-city/',
                                   {'s': 'name:Brasilia', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Brasilia')

    def test_act_collection_list(self):
        """Act collection list returns 200"""
        self.login_admin()
        ActCollection.objects.create(name='Colecao Teste', language='pt-br')

        response = self.client.get('/legislation/aux-act-collection/',
                                   {'s': 'name:Colecao', 'filter_owner': '*'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Colecao Teste')


class LeisRefSearchTest(BaseTestCase):
    def test_search_id(self):
        self.login_admin()

        scope_region = baker.make("leisref.ActCountryRegion")
        act_type = baker.make("leisref.ActType")
        baker.make("leisref.Act", scope_region=scope_region, act_type=act_type, id=1)
        baker.make("leisref.Act", scope_region=scope_region, act_type=act_type, id=2)
        baker.make("leisref.Act", scope_region=scope_region, act_type=act_type, id=3)

        resp1 = self.client.get("/legislation/", {"s": "id:1", "filter_owner": "*"})
        self.assertEqual(200, resp1.status_code)
        self.assertContains(resp1, '<a href="/legislation/edit/1">1</a')
        self.assertNotContains(resp1, '<a href="/legislation/edit/2">2</a')
        self.assertNotContains(resp1, '<a href="/legislation/edit/3">3</a')

        resp2 = self.client.get("/legislation/", {"s": "id:2", "filter_owner": "*"})
        self.assertEqual(200, resp2.status_code)
        self.assertContains(resp2, '<a href="/legislation/edit/2">2</a')
        self.assertNotContains(resp2, '<a href="/legislation/edit/1">1</a')
        self.assertNotContains(resp2, '<a href="/legislation/edit/3">3</a')

        resp3 = self.client.get("/legislation/", {"s": "id:3", "filter_owner": "*"})
        self.assertEqual(200, resp3.status_code)
        self.assertContains(resp3, '<a href="/legislation/edit/3">3</a')
        self.assertNotContains(resp3, '<a href="/legislation/edit/1">1</a')
        self.assertNotContains(resp3, '<a href="/legislation/edit/2">2</a')
