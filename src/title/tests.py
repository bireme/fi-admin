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
        self.assertEqual(Title.objects.all()[0].cooperative_center_code, "BR1.1")

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


class TitleListViewTest(BaseTestCase):
    """
    Tests for TitleListView filtering, search, ordering and context
    """

    def setUp(self):
        super(TitleListViewTest, self).setUp()
        self.country = Country.objects.create(code='BR', name='Brasil')

    def _create_title(self, user, title='Test Title', id_number='1',
                      shortened_title='Test', issn='', secs_number='',
                      cc='BR1.1'):
        """Helper to create a single Title with given attributes"""
        obj = Title.objects.create(
            id_number=id_number, status='C', title=title,
            shortened_title=shortened_title, creation_date='20200101',
            created_by=user, cooperative_center_code=cc,
            issn=issn, secs_number=secs_number
        )
        obj.country.add(self.country)
        return obj

    # --- 1. Search functionality ---

    def test_list_search_by_title(self):
        """Search ?s= matches title via icontains"""
        user = self.login_admin()

        self._create_title(user, title='Unique Medical Journal', id_number='1')
        self._create_title(user, title='Other Record', id_number='2')

        response = self.client.get('/title/', {'s': 'Unique Medical'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Medical Journal')
        self.assertNotContains(response, 'Other Record')

    def test_list_search_by_short_title(self):
        """Search ?short_title= matches shortened_title via icontains"""
        user = self.login_admin()

        self._create_title(user, title='Journal A', shortened_title='J. Med. A',
                           id_number='1')
        self._create_title(user, title='Journal B', shortened_title='J. Sci. B',
                           id_number='2')

        response = self.client.get('/title/', {'short_title': 'Med'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Journal A')
        self.assertNotContains(response, 'Journal B')

    def test_list_search_by_issn(self):
        """Search ?issn= filters by exact ISSN"""
        user = self.login_admin()

        self._create_title(user, title='ISSN Match', issn='1234-5678', id_number='1')
        self._create_title(user, title='ISSN No Match', issn='8765-4321', id_number='2')

        response = self.client.get('/title/', {'issn': '1234-5678'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ISSN Match')
        self.assertNotContains(response, 'ISSN No Match')

    def test_list_search_by_secs_number(self):
        """Search ?secs_number= filters by exact secs_number"""
        user = self.login_admin()

        self._create_title(user, title='SECS Match', secs_number='S001', id_number='1')
        self._create_title(user, title='SECS No Match', secs_number='S002', id_number='2')

        response = self.client.get('/title/', {'secs_number': 'S001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SECS Match')
        self.assertNotContains(response, 'SECS No Match')

    def test_list_search_by_id_number(self):
        """Search ?id= filters by id_number"""
        user = self.login_admin()

        self._create_title(user, title='ID Match', id_number='100')
        self._create_title(user, title='ID No Match', id_number='200')

        response = self.client.get('/title/', {'id': '100'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ID Match')
        self.assertNotContains(response, 'ID No Match')

    def test_list_empty_search_returns_all(self):
        """Empty search string returns all records"""
        user = self.login_admin()

        self._create_title(user, title='Title One', id_number='1')
        self._create_title(user, title='Title Two', id_number='2')

        response = self.client.get('/title/', {'s': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Title One')
        self.assertContains(response, 'Title Two')

    # --- 2. Ordering ---

    def test_list_ordering(self):
        """order=- with orderby applies descending sort"""
        user = self.login_admin()

        self._create_title(user, title='AAA Journal', id_number='1')
        self._create_title(user, title='ZZZ Journal', id_number='2')

        response = self.client.get('/title/', {'order': '-', 'orderby': 'title'})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        pos_zzz = content.find('ZZZ Journal')
        pos_aaa = content.find('AAA Journal')
        self.assertGreater(pos_zzz, -1)
        self.assertGreater(pos_aaa, -1)
        self.assertLess(pos_zzz, pos_aaa)

    # --- 3. Context data ---

    def test_list_context_data(self):
        """Context contains expected keys"""
        self.login_admin()

        response = self.client.get('/title/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('actions', response.context)

    # --- 4. Access control ---

    def test_list_unauthenticated_redirects(self):
        """Unauthenticated access redirects to login"""
        response = self.client.get('/title/')
        self.assertEqual(response.status_code, 302)


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
