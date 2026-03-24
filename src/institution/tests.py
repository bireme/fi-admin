#-*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User
from django.core.cache import cache
from model_bakery import baker

from .models import *
from utils.models import Country
from utils.tests import BaseTestCase


def login_admin_institution(test_case):
    '''
    Login as admin and add user_type=advanced required by institution views
    '''
    user = test_case.login_admin()
    data = json.loads(user.profile.data)
    data['user_type'] = 'advanced'
    user.profile.data = json.dumps(data)
    user.profile.save()
    cache.clear()
    return user


def minimal_form_data(country_id):
    '''
    Define minimal fields for submitting an Institution form
    '''
    form_data = {
        'status': '1',
        'cc_code': 'BR1.1',
        'name': 'Test Institution',
        'country': str(country_id),

        'contact_set-TOTAL_FORMS': '0',
        'contact_set-INITIAL_FORMS': '0',

        'url_set-TOTAL_FORMS': '0',
        'url_set-INITIAL_FORMS': '0',

        'unitlevel_set-TOTAL_FORMS': '0',
        'unitlevel_set-INITIAL_FORMS': '0',

        'adm_set-TOTAL_FORMS': '1',
        'adm_set-INITIAL_FORMS': '0',
    }

    return form_data


def create_institution_object(user, country):
    '''
    Create Institution objects for tests
    '''
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

    inst1 = Institution.objects.create(
        cc_code='BR1.1', name='Institution Brasil',
        status=1, country=country,
        cooperative_center_code='BR1.1', created_by=user
    )
    Contact.objects.create(institution=inst1, name='Contact One',
                           email='contact@test.com')
    URL.objects.create(institution=inst1, url_type='main',
                       url='http://inst1.example.com')

    inst2 = Institution.objects.create(
        cc_code='PY3.1', name='Institution Paraguay',
        status=1, country=country,
        cooperative_center_code='PY3.1', created_by=user2
    )

    return inst1, inst2


class InstitutionTest(BaseTestCase):
    """
    Tests for institution app
    """

    def setUp(self):
        super(InstitutionTest, self).setUp()

        self.country = Country.objects.create(code='BR', name='Brazil')

    def test_list_institution(self):
        """
        Test list Institution
        """
        user = login_admin_institution(self)
        create_institution_object(user, self.country)

        response = self.client.get('/institution/')
        self.assertContains(response, "Institution Brasil")

        # default filter_owner filters by cc_code=user_cc (BR1.1)
        self.assertNotContains(response, "Institution Paraguay")

    def test_add_institution(self):
        """
        Tests create Institution
        """
        login_admin_institution(self)

        form_data = minimal_form_data(self.country.id)
        form_data['cc_code'] = 'XX9.9'
        form_data['name'] = 'New Test Institution'

        response = self.client.post('/institution/new', form_data, follow=True)
        self.assertRedirects(response, '/institution/')

        # verify institution was created
        self.assertTrue(Institution.objects.filter(cc_code='XX9.9').exists())

    def test_edit_institution(self):
        """
        Tests edit Institution
        """
        user = login_admin_institution(self)
        inst1, inst2 = create_institution_object(user, self.country)

        url = '/institution/edit/{0}'.format(inst1.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, inst1.name)

        # Test changes values and submit
        form_data = minimal_form_data(self.country.id)
        form_data['cc_code'] = inst1.cc_code
        form_data['name'] = 'Institution Edited'
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/institution/')
        self.assertContains(response, "Institution Edited")

    def test_delete_institution(self):
        """
        Tests delete Institution
        """
        user = login_admin_institution(self)
        inst1, inst2 = create_institution_object(user, self.country)

        response = self.client.get('/institution/delete/{0}'.format(inst1.id))
        # confirm page shows institution details
        self.assertContains(response, inst1.cc_code)

        response = self.client.post('/institution/delete/{0}'.format(inst1.id))

        self.assertTrue(Institution.objects.filter(id=inst1.id).count() == 0)
        self.assertTrue(Contact.objects.filter(institution_id=inst1.id).count() == 0)
        self.assertTrue(URL.objects.filter(institution_id=inst1.id).count() == 0)
        self.assertTrue(Adm.objects.filter(institution_id=inst1.id).count() == 0)

        self.assertRedirects(response, '/institution/')


class InstitutionSearchTest(BaseTestCase):
    def test_search_cc_code(self):
        """
        Test search by CC code pattern (e.g. 'AA1') which uses cc_code__istartswith
        """
        user = login_admin_institution(self)
        country = Country.objects.create(code='BR', name='Brazil')

        Institution.objects.create(
            cc_code='AA1.1', name='Alpha Center', status=1,
            country=country, cooperative_center_code='BR1.1', created_by=user
        )
        Institution.objects.create(
            cc_code='BB2.2', name='Beta Center', status=1,
            country=country, cooperative_center_code='BR1.1', created_by=user
        )

        resp = self.client.get("/institution/", {"s": "AA1", "filter_owner": "*"})
        self.assertEqual(200, resp.status_code)
        self.assertContains(resp, "Alpha Center")
        self.assertNotContains(resp, "Beta Center")

        resp2 = self.client.get("/institution/", {"s": "BB2", "filter_owner": "*"})
        self.assertEqual(200, resp2.status_code)
        self.assertContains(resp2, "Beta Center")
        self.assertNotContains(resp2, "Alpha Center")
