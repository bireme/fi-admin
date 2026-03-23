#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from model_bakery import baker

from .models import *
from main.models import Descriptor, ResourceThematic, ThematicArea
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
        self.assertEquals(Act.objects.all()[0].cooperative_center_code, "BR1.1")

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
