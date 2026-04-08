# coding: utf-8
"""
Smoke tests for Tastypie API endpoints.

Purpose: provide a minimal regression safety net for the Django upgrade
(see .ai/plans/001-upgrade-django-to-5.2.md item 1.4 and
.ai/plans/015-api-endpoint-tests.md). These tests verify that each
Tastypie resource is properly wired, that list endpoints return the
standard Tastypie envelope, and that method restrictions and
authentication behave as configured.

Custom prepend_urls endpoints that call external search services
(get_search / get_next / get_last_id) are intentionally NOT covered.
"""
import json

from django.contrib.auth.models import User
from model_bakery import baker
from tastypie.models import ApiKey

from utils.tests import BaseTestCase


class ApiTestBase(BaseTestCase):
    """Shared helpers for Tastypie endpoint tests."""

    def get_json(self, url, **extra):
        response = self.client.get(url, **extra)
        return response

    def assert_list_envelope(self, response):
        """A Tastypie list endpoint returns JSON with meta + objects keys."""
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'].split(';')[0], 'application/json')
        payload = json.loads(response.content.decode('utf-8'))
        self.assertIn('meta', payload)
        self.assertIn('objects', payload)
        return payload


# ---------------------------------------------------------------------------
# bibliographic — /api/bibliographic/
# ---------------------------------------------------------------------------
class BibliographicApiTests(ApiTestBase):
    """
    ReferenceResource has a complex dehydrate that depends on child
    class (Analytic/Source) plus attachments, descriptors and related
    resources. The smoke test only exercises the empty-list path and
    method restriction — creating a fully valid Reference fixture is
    the concern of biblioref/tests.py.
    """
    url = '/api/bibliographic/'

    def test_list_empty_returns_200(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 0)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# event — /api/event/
# ---------------------------------------------------------------------------
class EventApiTests(ApiTestBase):
    url = '/api/event/'

    def setUp(self):
        super().setUp()
        # queryset filters status=1
        self.event = baker.make('events.Event', status=1, title='API test event')

    def test_list_returns_created_event(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)
        self.assertEqual(payload['objects'][0]['title'], 'API test event')

    def test_detail_returns_200(self):
        response = self.client.get('{}{}/'.format(self.url, self.event.pk))
        self.assertEqual(response.status_code, 200)

    def test_detail_missing_returns_404(self):
        response = self.client.get('{}999999/'.format(self.url))
        self.assertEqual(response.status_code, 404)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# multimedia — /api/multimedia/
# ---------------------------------------------------------------------------
class MultimediaApiTests(ApiTestBase):
    url = '/api/multimedia/'

    def setUp(self):
        super().setUp()
        # queryset filters status=1; dehydrate splits authors/contributors/related_links
        self.media = baker.make(
            'multimedia.Media',
            status=1,
            title='API test media',
            authors='',
            contributors='',
            related_links='',
        )

    def test_list_returns_created_media(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)

    def test_detail_returns_200(self):
        response = self.client.get('{}{}/'.format(self.url, self.media.pk))
        self.assertEqual(response.status_code, 200)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# oer — /api/oer/  (ApiKeyAuthentication on POST; GET is public)
# ---------------------------------------------------------------------------
class OerApiTests(ApiTestBase):
    url = '/api/oer/'

    def setUp(self):
        super().setUp()
        self.oer = baker.make('oer.OER', status=1, title='API test oer')
        self.user = User.objects.create_user('oer_api_user', 'oer@test.com', 'oer')
        self.api_key = ApiKey.objects.create(user=self.user)

    def test_list_get_is_public(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)

    def test_post_without_credentials_returns_401(self):
        # POST triggers ApiKeyAuthentication
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_post_with_api_key_is_authenticated(self):
        response = self.client.post(
            '{}?username={}&api_key={}'.format(self.url, self.user.username, self.api_key.key),
            data='{}',
            content_type='application/json',
        )
        # 401 would mean auth failed; any other status means we got past the
        # ApiKeyAuthentication gate (tastypie may still reject an empty body)
        self.assertNotEqual(response.status_code, 401)


# ---------------------------------------------------------------------------
# leisref — /api/leisref/
# ---------------------------------------------------------------------------
class LeisrefApiTests(ApiTestBase):
    url = '/api/leisref/'

    def setUp(self):
        super().setUp()
        self.act = baker.make('leisref.Act', status=1)

    def test_list_returns_created_act(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)

    def test_detail_returns_200(self):
        response = self.client.get('{}{}/'.format(self.url, self.act.pk))
        self.assertEqual(response.status_code, 200)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# title — /api/title/
# ---------------------------------------------------------------------------
class TitleApiTests(ApiTestBase):
    url = '/api/title/'

    def setUp(self):
        super().setUp()
        self.title = baker.make('title.Title')

    def test_list_returns_created_title(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# institution — /api/institution/
# ---------------------------------------------------------------------------
class InstitutionApiTests(ApiTestBase):
    url = '/api/institution/'

    def setUp(self):
        super().setUp()
        self.institution = baker.make('institution.Institution')

    def test_list_returns_created_institution(self):
        payload = self.assert_list_envelope(self.client.get(self.url))
        self.assertEqual(payload['meta']['total_count'], 1)

    def test_post_not_allowed(self):
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# classification — /api/community/, /api/collection/, /api/classification/
# ---------------------------------------------------------------------------
class ClassificationApiTests(ApiTestBase):
    def setUp(self):
        super().setUp()
        # A community is a top-level Collection (community_flag=True, no parent)
        self.community = baker.make(
            'classification.Collection',
            community_flag=True,
            parent=None,
            language='en',
            image='',
        )
        # A collection is a child Collection (parent set)
        self.collection = baker.make(
            'classification.Collection',
            community_flag=False,
            parent=self.community,
            language='en',
            image='',
        )

    def test_community_list_returns_200(self):
        payload = self.assert_list_envelope(self.client.get('/api/community/'))
        self.assertGreaterEqual(payload['meta']['total_count'], 1)

    def test_collection_list_returns_200(self):
        payload = self.assert_list_envelope(self.client.get('/api/collection/'))
        self.assertGreaterEqual(payload['meta']['total_count'], 1)

    def test_classification_list_returns_200(self):
        # Relationship queryset is empty — smoke-check the envelope only
        self.assert_list_envelope(self.client.get('/api/classification/'))

    def test_post_not_allowed(self):
        response = self.client.post('/api/community/', data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 405)


# ---------------------------------------------------------------------------
# thesaurus JSON endpoints — /api/desc/, /api/qualif/, /api/ths/
# ---------------------------------------------------------------------------
class ThesaurusApiTests(ApiTestBase):
    """
    Thesaurus resources read from the `decs_portal` database and require
    a `ths` filter to return rows. The smoke test exercises the URL
    dispatch and resource instantiation only — no fixtures are created
    because the data lives in an external DB not present in the test
    environment.
    """

    def _assert_responds(self, url):
        response = self.client.get(url)
        # 200 with empty envelope is the expected happy path; any non-5xx
        # response means URL dispatch + resource instantiation worked.
        self.assertLess(response.status_code, 500)

    def test_desc_endpoint_responds(self):
        self._assert_responds('/api/desc/thesaurus/')

    def test_qualif_endpoint_responds(self):
        self._assert_responds('/api/qualif/thesaurus/')

    def test_ths_endpoint_responds(self):
        self._assert_responds('/api/ths/thesaurus/')
