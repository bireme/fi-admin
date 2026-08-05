# coding: utf-8
"""
Smoke tests for Tastypie API endpoints.

Purpose: provide a minimal regression safety net for the Django upgrade
(see .ai/plans/001-upgrade-django-to-5.2.md item 1.4 and
.ai/plans/015-api-endpoint-tests.md). These tests verify that each
Tastypie resource is properly wired, that list endpoints return the
standard Tastypie envelope, and that method restrictions and
authentication behave as configured.

The `search` endpoints talk to an external service through
`api.search_service`; they are covered by SearchServiceTests and
SearchEndpointTests below, with the HTTP call mocked. `get_last_id`
is still not covered.
"""
import json
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from lxml.etree import tostring
from model_bakery import baker
from tastypie.models import ApiKey

from api import search_service
from api.search_service import (
    duplicate_response_to_match,
    get_search_headers,
    search_service_request,
)
from api.ws_decs_serializer import WsDecsSerializer
from utils.tests import BaseTestCase


def make_search_response(status_code=200, json_data=None, raise_value_error=False):
    """Build a stand-in for the `requests` Response returned by the search service."""
    response = mock.Mock()
    response.status_code = status_code
    if raise_value_error:
        response.json.side_effect = ValueError('No JSON object could be decoded')
    else:
        response.json.return_value = json_data
    return response


def solr_payload(num_found=1, docs=None):
    """Minimal shape of a successful `search_json` response."""
    return {'diaServerResponse': [{
        'response': {'numFound': num_found, 'docs': docs if docs is not None else [{'id': 'doc-1'}]},
    }]}


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

    @override_settings(APP_VERSION="9.8.7-test")
    def test_detail_reports_system_version_from_settings(self):
        # literature_type/publication_date_normalized are read by
        # ReferenceSource.__str__ during serialization
        reference = baker.make(
            'biblioref.ReferenceSource',
            treatment_level='m',
            literature_type='S',
            title_serial='API test serial',
            publication_date_normalized='20260101',
            status=1,
        )

        response = self.client.get('{}{}/'.format(self.url, reference.pk))
        self.assertEqual(response.status_code, 200)

        payload = json.loads(response.content.decode('utf-8'))
        self.assertEqual(payload['system_version'], '9.8.7-test')


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

    def test_filter_by_indexed_database(self):
        db = baker.make('leisref.Database', acronym='LILACS', name='LILACS')
        act_indexed = baker.make('leisref.Act', status=1)
        act_indexed.indexed_database.add(db)
        act_not_indexed = baker.make('leisref.Act', status=1)

        response = self.client.get('{}?indexed_database=LILACS'.format(self.url))
        payload = self.assert_list_envelope(response)
        returned_ids = [obj['id'] for obj in payload['objects']]
        self.assertIn(act_indexed.pk, returned_ids)
        self.assertNotIn(act_not_indexed.pk, returned_ids)


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


# ---------------------------------------------------------------------------
# api.search_service — shared client for the external search service
# ---------------------------------------------------------------------------
@override_settings(
    SEARCH_SERVICE_URL='http://search.test',
    SEARCH_SERVICE_APIKEY='test-apikey',
    SEARCH_INDEX='solr/fi-admin',
)
class SearchServiceTests(TestCase):
    """
    Regression cover for the 403 documented in
    .ai/logs/2026-08-05-fix-bibliographic-search-403.md: the service is
    fronted by nginx that rejects the request unless an explicit
    Content-Type and a non-default User-Agent are sent.
    """

    def test_headers_include_apikey_content_type_and_user_agent(self):
        headers = get_search_headers()
        self.assertEqual(headers['apikey'], 'test-apikey')
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['User-Agent'], 'fi-admin')

    def test_user_agent_is_not_the_requests_default(self):
        # `python-requests/*` and `curl/*` are blocklisted by the service
        user_agent = get_search_headers()['User-Agent']
        self.assertNotIn('python-requests', user_agent)
        self.assertNotIn('curl', user_agent)

    def test_headers_follow_settings_at_call_time(self):
        with override_settings(SEARCH_SERVICE_APIKEY='rotated-key'):
            self.assertEqual(get_search_headers()['apikey'], 'rotated-key')

    def test_request_posts_json_body_with_required_headers(self):
        with mock.patch.object(search_service.requests, 'post',
                               return_value=make_search_response(json_data=solr_payload())) as post:
            search_service_request({'q': 'malaria', 'count': 5})

        args, kwargs = post.call_args
        self.assertEqual(args[0], 'http://search.test/search_json')
        # the body must be a JSON-encoded string, not a form-encoded dict
        self.assertEqual(json.loads(kwargs['data']), {'q': 'malaria', 'count': 5})
        self.assertEqual(kwargs['headers']['apikey'], 'test-apikey')
        self.assertEqual(kwargs['headers']['Content-Type'], 'application/json')
        self.assertEqual(kwargs['headers']['User-Agent'], 'fi-admin')

    def test_request_returns_decoded_json(self):
        payload = solr_payload(num_found=42)
        with mock.patch.object(search_service.requests, 'post',
                               return_value=make_search_response(json_data=payload)):
            result = search_service_request({'q': 'a'})

        self.assertEqual(result['diaServerResponse'][0]['response']['numFound'], 42)

    def test_non_json_response_returns_error_payload_with_status(self):
        # a 403 from nginx is an HTML page: must not raise, must report the status
        with mock.patch.object(search_service.requests, 'post',
                               return_value=make_search_response(403, raise_value_error=True)):
            result = search_service_request({'q': 'a'})

        self.assertEqual(result['type'], 'error')
        self.assertIn('403', result['message'])

    def test_duplicate_response_to_match_copies_response(self):
        payload = duplicate_response_to_match(solr_payload(num_found=7))
        server_response = payload['diaServerResponse'][0]
        self.assertEqual(server_response['match'], server_response['response'])

    def test_duplicate_response_to_match_ignores_error_payload(self):
        # error payloads have no diaServerResponse — must not raise KeyError
        error = {'type': 'error', 'message': 'invalid output (status 403)'}
        self.assertEqual(duplicate_response_to_match(error), error)

    def test_duplicate_response_to_match_ignores_empty_payload(self):
        self.assertIsNone(duplicate_response_to_match(None))


# ---------------------------------------------------------------------------
# search endpoints — every resource exposing /search/
# ---------------------------------------------------------------------------
@override_settings(
    SEARCH_SERVICE_URL='http://search.test',
    SEARCH_SERVICE_APIKEY='test-apikey',
    SEARCH_INDEX='solr/fi-admin',
)
class SearchEndpointTests(ApiTestBase):
    """
    Exercises each registered `search` endpoint with the external HTTP call
    mocked, so the wiring (URL dispatch -> search_service -> response) is
    covered without touching the network.
    """

    # (label, url) for every routed search endpoint
    SEARCH_URLS = [
        ('bibliographic', '/api/bibliographic/search/'),
        ('resource', '/api/resource/search/'),
        ('event', '/api/event/search/'),
        ('event_next', '/api/event/next/'),
        ('multimedia', '/api/multimedia/search/'),
        ('title', '/api/title/search/'),
        ('leisref', '/api/leisref/search/'),
        ('oer', '/api/oer/search/'),
        ('institution', '/api/institution/search/'),
        ('thesaurus_desc', '/api/descriptors/thesaurus/search/'),
        ('thesaurus_qualif', '/api/qualifiers/thesaurus/search/'),
        ('thesaurus_desc_api', '/api/desc/thesaurus/search/'),
        ('thesaurus_qualif_api', '/api/qualif/thesaurus/search/'),
        ('thesaurus_desc_index', '/api/desc/index/thesaurus/search/'),
        ('thesaurus_qualif_index', '/api/qualif/index/thesaurus/search/'),
    ]

    def test_all_search_endpoints_return_service_payload(self):
        for label, url in self.SEARCH_URLS:
            with self.subTest(endpoint=label):
                with mock.patch.object(
                    search_service.requests, 'post',
                    return_value=make_search_response(json_data=solr_payload(num_found=3)),
                ):
                    response = self.client.get(url, {'q': 'malaria', 'count': 1})

                self.assertEqual(response.status_code, 200)
                payload = json.loads(response.content.decode('utf-8'))
                self.assertEqual(payload['diaServerResponse'][0]['response']['numFound'], 3)

    def test_all_search_endpoints_send_required_headers(self):
        for label, url in self.SEARCH_URLS:
            with self.subTest(endpoint=label):
                with mock.patch.object(
                    search_service.requests, 'post',
                    return_value=make_search_response(json_data=solr_payload()),
                ) as post:
                    self.client.get(url, {'q': 'malaria', 'count': 1})

                headers = post.call_args.kwargs['headers']
                self.assertEqual(headers['apikey'], 'test-apikey')
                self.assertEqual(headers['Content-Type'], 'application/json')
                self.assertNotIn('python-requests', headers['User-Agent'])

    def test_all_search_endpoints_survive_a_403(self):
        """A blocked request must surface an error payload, never a 500."""
        for label, url in self.SEARCH_URLS:
            with self.subTest(endpoint=label):
                with mock.patch.object(
                    search_service.requests, 'post',
                    return_value=make_search_response(403, raise_value_error=True),
                ):
                    response = self.client.get(url, {'q': 'malaria', 'id': 'doc-1'})

                self.assertEqual(response.status_code, 200)
                payload = json.loads(response.content.decode('utf-8'))
                self.assertEqual(payload['type'], 'error')
                self.assertIn('403', payload['message'])

    def test_search_forwards_query_params_to_service(self):
        with mock.patch.object(
            search_service.requests, 'post',
            return_value=make_search_response(json_data=solr_payload()),
        ) as post:
            self.client.get('/api/bibliographic/search/', {'q': 'dengue', 'count': 7, 'start': 2})

        sent = json.loads(post.call_args.kwargs['data'])
        self.assertEqual(sent['q'], 'dengue')
        self.assertEqual(sent['count'], 7)
        self.assertEqual(sent['start'], 2)
        self.assertEqual(sent['site'], 'solr/fi-admin')

    def test_bibliographic_search_filters_by_publication_status(self):
        with mock.patch.object(
            search_service.requests, 'post',
            return_value=make_search_response(json_data=solr_payload()),
        ) as post:
            self.client.get('/api/bibliographic/search/', {'q': 'dengue'})

        filter_query = json.loads(post.call_args.kwargs['data'])['fq'][0]
        self.assertIn('status:("-3" OR "0" OR "1")', filter_query)
        self.assertIn('django_ct:biblioref.reference*', filter_query)

    def test_search_by_id_duplicates_response_to_match(self):
        with mock.patch.object(
            search_service.requests, 'post',
            return_value=make_search_response(json_data=solr_payload()),
        ) as post:
            response = self.client.get('/api/bibliographic/search/', {'id': 'biblioref.reference.1'})

        # the id is turned into a q=id:<value> lookup
        self.assertEqual(json.loads(post.call_args.kwargs['data'])['q'], 'id:biblioref.reference.1')

        server_response = json.loads(response.content.decode('utf-8'))['diaServerResponse'][0]
        self.assertEqual(server_response['match'], server_response['response'])

    def test_search_without_id_has_no_match_element(self):
        with mock.patch.object(
            search_service.requests, 'post',
            return_value=make_search_response(json_data=solr_payload()),
        ):
            response = self.client.get('/api/bibliographic/search/', {'q': 'dengue'})

        server_response = json.loads(response.content.decode('utf-8'))['diaServerResponse'][0]
        self.assertNotIn('match', server_response)

    def test_bibliographic_search_forwards_facet_fields(self):
        with mock.patch.object(
            search_service.requests, 'post',
            return_value=make_search_response(json_data=solr_payload()),
        ) as post:
            self.client.get('/api/bibliographic/search/', {
                'q': 'dengue',
                'facet.field': 'publication_year',
                'f.publication_year.facet.limit': '5',
            })

        sent = json.loads(post.call_args.kwargs['data'])
        self.assertEqual(sent['facet.field'], ['publication_year'])
        self.assertEqual(sent['f.publication_year.facet.limit'], '5')


# ---------------------------------------------------------------------------
# WsDecsSerializer — validates six/force_text removal
# ---------------------------------------------------------------------------
class WsDecsSerializerTest(TestCase):

    def setUp(self):
        self.serializer = WsDecsSerializer()

    def test_to_etree_string_value(self):
        element = self.serializer.to_etree('hello', name='term')
        self.assertEqual(element.tag, 'term')
        self.assertEqual(element.text, 'hello')

    def test_to_etree_integer_value(self):
        element = self.serializer.to_etree(42, name='count')
        self.assertEqual(element.tag, 'count')
        self.assertEqual(element.text, '42')

    def test_to_etree_none_value(self):
        element = self.serializer.to_etree(None, name='empty')
        self.assertEqual(element.tag, 'empty')
        self.assertIsNone(element.text)

    def test_to_etree_unicode_value(self):
        element = self.serializer.to_etree(u'café é', name='term')
        self.assertEqual(element.text, u'café é')

    def test_to_etree_dict(self):
        data = {'name': 'test', 'value': 'abc'}
        element = self.serializer.to_etree(data, name='root', depth=1)
        self.assertEqual(element.tag, 'root')
        children = {child.tag: child.text for child in element}
        self.assertEqual(children['name'], 'test')
        self.assertEqual(children['value'], 'abc')

    def test_to_etree_list(self):
        data = ['a', 'b']
        element = self.serializer.to_etree(data, name='items')
        self.assertEqual(element.tag, 'items')
        self.assertEqual(len(element), 2)

    def test_to_etree_dict_with_attr_key(self):
        data = {'attr': {'lang': 'en'}, 'text': 'hello'}
        element = self.serializer.to_etree(data, name='item', depth=1)
        self.assertEqual(element.get('lang'), 'en')

    def test_to_etree_boolean_value(self):
        element = self.serializer.to_etree(True, name='flag')
        self.assertEqual(element.tag, 'flag')
        self.assertEqual(element.text, 'True')
