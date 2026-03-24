#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from model_bakery import baker

from .models import *
from main.models import Descriptor, Keyword
from utils.models import Country
from utils.tests import BaseTestCase


def minimal_form_data(country_id):
    '''
    Define minimal fields for submitting a Title form.
    Includes 1 descriptor (required by DescriptorRequired formset).
    '''
    form_data = {
        'status': 'C',
        'title': 'Revista de teste',
        'shortened_title': 'Rev. teste',
        'creation_date': '20200101',
        'initial_date': '2020',
        'state': 'SP',
        'country': [str(country_id)],
        'action': 'save',

        # Descriptor formset - at least 1 required
        'main-descriptor-content_type-object_id-TOTAL_FORMS': '1',
        'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',
        'main-descriptor-content_type-object_id-0-id': '',
        'main-descriptor-content_type-object_id-0-text': 'malaria',
        'main-descriptor-content_type-object_id-0-code': '^d8462',
        'main-descriptor-content_type-object_id-0-status': '0',

        # Keyword formset
        'main-keyword-content_type-object_id-TOTAL_FORMS': '0',
        'main-keyword-content_type-object_id-INITIAL_FORMS': '0',

        # OnlineResources formset
        'onlineresources_set-TOTAL_FORMS': '0',
        'onlineresources_set-INITIAL_FORMS': '0',

        # TitleVariance formset
        'titlevariance_set-TOTAL_FORMS': '0',
        'titlevariance_set-INITIAL_FORMS': '0',

        # BVSSpecialty formset
        'bvsspecialty_set-TOTAL_FORMS': '0',
        'bvsspecialty_set-INITIAL_FORMS': '0',

        # IndexRange formset
        'indexrange_set-TOTAL_FORMS': '0',
        'indexrange_set-INITIAL_FORMS': '0',

        # Audit formset
        'audit_set-TOTAL_FORMS': '0',
        'audit_set-INITIAL_FORMS': '0',

        # Issue formset
        'issue_set-TOTAL_FORMS': '0',
        'issue_set-INITIAL_FORMS': '0',

        # Collection formset
        'collection_set-TOTAL_FORMS': '0',
        'collection_set-INITIAL_FORMS': '0',

        # PublicInfo formset
        'publicinfo_set-TOTAL_FORMS': '0',
        'publicinfo_set-INITIAL_FORMS': '0',
    }

    return form_data


def create_title_object(user, country):
    '''
    Create Title objects for tests
    '''
    user2 = User.objects.create_user('user2', 'user2@test.com', 'user2')

    title1 = Title.objects.create(
        id_number='1', status='C', title='Revista de teste (BR1.1)',
        shortened_title='Rev. teste BR', creation_date='20200101',
        created_by=user, cooperative_center_code='BR1.1'
    )
    title1.country.add(country)

    title_ct = ContentType.objects.get_for_model(title1)
    Descriptor.objects.create(object_id=title1.id, content_type=title_ct, text='malaria')

    title2 = Title.objects.create(
        id_number='2', status='C', title='Revista de prueba (PY3.1)',
        shortened_title='Rev. prueba PY', creation_date='20200101',
        created_by=user2, cooperative_center_code='PY3.1'
    )
    title2.country.add(country)

    return title1, title2


class TitleTest(BaseTestCase):
    """
    Tests for title app
    """

    def setUp(self):
        super(TitleTest, self).setUp()

        # create auxiliary models used on tests
        self.country = Country.objects.create(code='BR', name='Brasil')

        # create a seed title so TitleForm.save() auto-id logic works
        # (Title.objects.latest('id') raises DoesNotExist on empty table)
        seed = Title.objects.create(
            id_number='0', status='C', title='Seed',
            shortened_title='Seed', creation_date='20200101',
            cooperative_center_code='BR1.1'
        )
        seed.country.add(self.country)

    def test_list_title(self):
        """
        Test list titles
        """
        user = self.login_admin()
        create_title_object(user, self.country)

        response = self.client.get('/title/')
        # no owner filtering in title list view (commented out)
        self.assertContains(response, "Revista de teste (BR1.1)")
        self.assertContains(response, "Revista de prueba (PY3.1)")

    def test_add_title(self):
        """
        Tests create title
        """
        self.login_admin()

        form_data = minimal_form_data(self.country.id)

        response = self.client.post('/title/new', form_data, follow=True)
        self.assertRedirects(response, '/title/')
        self.assertContains(response, "Revista de teste")

        # check if cooperative center code is set from user profile (admin = BR1.1)
        self.assertEquals(Title.objects.all()[0].cooperative_center_code, "BR1.1")

    def test_edit_title(self):
        """
        Tests edit title
        """
        user = self.login_admin()
        title1, title2 = create_title_object(user, self.country)

        url = '/title/edit/{0}'.format(title1.id)
        response = self.client.get(url)

        # Test if return form with fields
        self.assertContains(response, title1.title)

        # Test changes values and submit
        form_data = minimal_form_data(self.country.id)
        form_data['title'] = 'Revista editada'
        form_data['shortened_title'] = 'Rev. editada'
        response = self.client.post(url, form_data, follow=True)
        self.assertRedirects(response, '/title/')
        self.assertContains(response, "Revista editada")

    def test_delete_title(self):
        """
        Tests delete title
        """
        user = self.login_admin()
        title1, title2 = create_title_object(user, self.country)

        response = self.client.get('/title/delete/{0}'.format(title1.id))
        self.assertContains(response, "Você tem certeza que deseja apagar?")

        response = self.client.post('/title/delete/{0}'.format(title1.id))

        self.assertTrue(Title.objects.filter(id=title1.id).count() == 0)

        title_ct = ContentType.objects.get_for_model(Title)
        self.assertTrue(Descriptor.objects.filter(object_id=title1.id, content_type=title_ct).count() == 0)
        self.assertTrue(Keyword.objects.filter(object_id=title1.id, content_type=title_ct).count() == 0)

        self.assertRedirects(response, '/title/')


class TitleSearchTest(BaseTestCase):
    def test_search_id(self):
        self.login_admin()

        country = baker.make("utils.Country")
        t1 = baker.make("title.Title", id_number='100', country=[country])
        t2 = baker.make("title.Title", id_number='200', country=[country])
        t3 = baker.make("title.Title", id_number='300', country=[country])

        resp1 = self.client.get("/title/", {"id": "100"})
        self.assertEqual(200, resp1.status_code)
        self.assertContains(resp1, '100')
        self.assertNotContains(resp1, '<a href="/title/edit/{0}">200</a'.format(t2.id))
        self.assertNotContains(resp1, '<a href="/title/edit/{0}">300</a'.format(t3.id))

        resp2 = self.client.get("/title/", {"id": "200"})
        self.assertEqual(200, resp2.status_code)
        self.assertContains(resp2, '200')
        self.assertNotContains(resp2, '<a href="/title/edit/{0}">100</a'.format(t1.id))
        self.assertNotContains(resp2, '<a href="/title/edit/{0}">300</a'.format(t3.id))
