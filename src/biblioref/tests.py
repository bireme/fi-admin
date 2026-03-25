# coding: utf-8
from unittest import skip

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from django.test.utils import override_settings
from model_bakery import baker

from biblioref.models import *
from database.models import Database
from main.models import Descriptor, ResourceThematic, ThematicArea
from title.models import Title
from utils.models import AuxCode
from utils.tests import BaseTestCase

form_data = {}

form_data['S'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title_serial': 'Rev. Enfermagem',
    'volume_serial': '10',
    'issue_number': '2',
}

form_data['Sas'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title': '[{"text": "Primeira analítica", "_i": "pt"}]',
    'english_translated_title': 'Hello World',
    'individual_author': '[{"text": "Chaves, Juca"}]'
}

form_data['Mm'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title_monographic': '[{"text": "Primeira monografia", "_i": "pt"}]',
    'individual_author_monographic': '[{"text": "Chaves, Juca"}]',
    'english_title_monographic': 'First monographic',
    'record_type': 'a',
    'text_language': 'pt',
    'publisher': 'EDITORA ABC',
    'publication_date': '2016 mai',
    'publication_date_normalized': '20160501',
    'publication_city': 'São Paulo',
    'publication_country': 1,
}

form_data['Mam'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title': '[{"text": "Primeira analítica da primeira monografia", "_i": "pt"}]',
    'english_translated_title': 'Transled title',
    'text_language': 'pt',
    'individual_author': '[{"text": "Chaves, Juca"}]',
    'record_type': 'a',
}

form_data['Tm'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title_monographic': '[{"text": "Primeira tese", "_i": "pt"}]',
    'individual_author_monographic': '[{"text": "Chaves, Juca"}]',
    'english_title_monographic': 'Transled title',
    'electronic_address': '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]',
    'record_type': 'a',
    'text_language': 'pt',
    'publisher': 'EDITORA USP',
    'publication_date': '2016 mai',
    'publication_date_normalized': '20160501',
    'publication_city': 'São Paulo',
    'publication_country': 1,
}

form_data['Tam'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title': '[{"text": "Primeira analítica de tese", "_i": "pt"}]',
    'english_translated_title': 'Transled title',
    'individual_author': '[{"text": "Chaves, Juca"}]',
    'text_language': 'pt',
    'record_type': 'a',
}

form_data['Mc'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title_collection': '[{"text": "Primeiro registro de coleção de monografias", "_i": "pt"}]',
    'english_title_collection': 'First monographic',
    'individual_author_collection': '[{"text": "Chaves, Juca"}]',
    'record_type': 'a',
    'text_language': 'pt',
    'publisher': 'EDITORA ABC',
    'publication_date': '2016 mai',
    'publication_date_normalized': '20160501',
    'publication_city': 'São Paulo',
    'publication_country': 1,
}

form_data['Mmc'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title_collection': '[{"text": "Registro fonte do tipo Monografia pertencente a uma coleção", "_i": "pt"}]',
    'individual_author_collection': '[{"text": "Chaves, Juca"}]',
    'english_title_collection': 'First monographic',
    'individual_author_collection': '[{"text": "Chaves, Juca"}]',
    'title_monographic': '[{"text": "Título nivel monografico", "_i": "pt"}]',
    'english_title_monographic': 'Hello World',
    'individual_author_monographic': '[{"text": "Chaves, Juca"}]',
    'record_type': 'a',
    'text_language': 'pt',
    'publisher': 'EDITORA ABC',
    'publication_date': '2016 mai',
    'publication_date_normalized': '20160501',
    'publication_city': 'São Paulo',
    'publication_country': 1,
}

form_data['Mamc'] = {
    'status': '-1',
    'LILACS_indexed': True,
    'indexed_database': 1,
    'title': '[{"text": "Primeira analítica", "_i": "pt"}]',
    'english_translated_title': 'Transled title',
    'text_language': 'pt',
    'individual_author': '[{"text": "Chaves, Juca"}]',
    'record_type': 'a',
}


blank_formsets = {
    'main-descriptor-content_type-object_id-TOTAL_FORMS': '0',
    'main-descriptor-content_type-object_id-INITIAL_FORMS': '0',

    'main-resourcethematic-content_type-object_id-TOTAL_FORMS': '0',
    'main-resourcethematic-content_type-object_id-INITIAL_FORMS': '0',

    'attachments-attachment-content_type-object_id-TOTAL_FORMS': '1',
    'attachments-attachment-content_type-object_id-INITIAL_FORMS': '0',

    'referencelocal_set-TOTAL_FORMS': '0',
    'referencelocal_set-INITIAL_FORMS': '0',

    'referencecomplement_set-TOTAL_FORMS': '1',
    'referencecomplement_set-INITIAL_FORMS': '0',
}

primary_descriptor = {
        'main-descriptor-content_type-object_id-TOTAL_FORMS': '1',

        'main-descriptor-content_type-object_id-0-id': '',
        'main-descriptor-content_type-object_id-0-text': 'malaria',
        'main-descriptor-content_type-object_id-0-code': '^d8462',
        'main-descriptor-content_type-object_id-0-primary': 1,
        'main-descriptor-content_type-object_id-0-status': '1',

}


@skip("Figure out why these tests are broken!")
class BiblioRefTest(BaseTestCase):
    """
    Tests for ref app
    """

    def setUp(self):
        super(BiblioRefTest, self).setUp()

        AuxCode.objects.create(code='pt', field='text_language', language='pt', label='Português')

        AuxCode.objects.create(code='a', field='record_type', language='pt', label='Material textual')

        AuxCode.objects.create(code='Doutorado', field='thesis_dissertation_academic_title', language='pt', label='Doutorado')

        Title.objects.create(id_number='1', record_type='KS', treatment_level='K', cooperative_center_code='BR1.1',
                             status='1', title='Revista de Enfermagem', creation_date='20160525',
                             shortened_title='Rev. Enfermagem', editor_cc_code='BR772', indexer_cc_code='BR1.1', issn='0000-XXXXX')

        Country.objects.create(code='BR', name='Brasil', LA_Caribbean=True)
        Database.objects.create(acronym='LILACS', regional_index=True)

    def test_editor_llxp(self):
        """
        Tests creation of records by editor llxp
        """
        self.login_editor_llxp()

        # test create new source
        post_data = form_data['S']
        post_data.update(blank_formsets)

        response = self.client.post('/bibliographic/new-source?document_type=S', post_data)
        # check for mandatory publication date
        self.assertContains(response, "O registro de informação neste campo está condicionado ao preenchimento do campo data de publicação")
        # add publication date
        post_data['publication_date'] = '2015 mai'
        post_data['publication_date_normalized'] = '20150501'
        response = self.client.post('/bibliographic/new-source?document_type=S', post_data)
        self.assertRedirects(response, '/bibliographic/new-analytic?source=1')

        # test create new analytic
        post_data = form_data['Sas']
        post_data.update(blank_formsets)
        response = self.client.post('/bibliographic/new-analytic?source=1', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')

        # test check for electronic_address or attachament
        post_data =  form_data['Sas']
        post_data.update(blank_formsets)
        post_data['status'] = 0
        post_data['text_language'] = 'pt'
        post_data.pop('english_translated_title', None)  # LLXP don't have this field
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        self.assertContains(response, "Endereço eletrônico OU texto completo obrigatório")

        # test publish record
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')

    def test_dataentry_monographic(self):
        """
        Tests creation of records by editor llxp
        """
        self.login_documentalist()

        # test create draft record
        post_data = form_data['Mm']
        post_data.update(blank_formsets)

        response = self.client.post('/bibliographic/new-source?document_type=Mm', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test list
        response = self.client.get('/bibliographic/')
        self.assertContains(response, 'Primeira monografia')

        # test edit and publish
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        # check validation of page or url
        self.assertContains(response, 'Endereço eletrônico, texto completo OU paginação obrigatório')
        # complete data and publish document
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test create new analytic
        post_data = form_data['Mam']
        post_data.update(blank_formsets)
        response = self.client.post('/bibliographic/new-analytic?source=1', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')
        # check if record is on the list
        response = self.client.get('/bibliographic/analytics?source=1')
        self.assertContains(response, 'Primeira analítica da primeira monografia')

        # test edit and publish analytic
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        # check validation of page or url
        self.assertContains(response, 'Endereço eletrônico, texto completo OU paginação obrigatório')
        # complete data and publish document
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')

    def test_dataentry_thesis(self):
        """
        Tests creation of records of type Thesis: source (Tm) and analytic (Tam)
        """
        self.login_documentalist()

        # test create new source draft
        post_data = form_data['Tm']
        post_data.update(blank_formsets)

        response = self.client.post('/bibliographic/new-source?document_type=Tm', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test edit and publish source
        post_data['status'] = 1

        post_data['thesis_dissertation_institution'] = 'USP'
        post_data['thesis_dissertation_academic_title'] = 'Invalido'
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        # check validation of thesis_dissertation_academic_title
        self.assertContains(response, 'Incompatível com a LILACS')
        post_data['thesis_dissertation_academic_title'] = 'Doutorado'
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test create new analytic
        post_data = form_data['Tam']
        post_data.update(blank_formsets)
        response = self.client.post('/bibliographic/new-analytic?source=1', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')
        # check if record is on the list
        response = self.client.get('/bibliographic/analytics?source=1')
        self.assertContains(response, 'Primeira analítica de tese')

        # test edit and publish analytic
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        # check validation of page or url
        self.assertContains(response, 'Endereço eletrônico, texto completo OU paginação obrigatório')
        # complete data and publish document
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')

    def test_dataentry_collection_of_monographs(self):
        """
        Tests creation of records of type Collection of Monographics (Mc)
        """
        self.login_documentalist()

        # test create new source draft
        post_data = form_data['Mc']
        post_data.update(blank_formsets)

        response = self.client.post('/bibliographic/new-source?document_type=Mc', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test edit and publish source
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        self.assertRedirects(response, '/bibliographic/')

    def test_dataentry_monographic_in_a_collecton(self):
        """
        Tests creation of records of type Monograph in a Collection (Mmc)
        """
        self.login_documentalist()

        # test create new source draft
        post_data = form_data['Mmc']
        post_data.update(blank_formsets)

        response = self.client.post('/bibliographic/new-source?document_type=Mmc', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test edit and publish source
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        # check validation of page or url
        self.assertContains(response, 'Endereço eletrônico, texto completo OU paginação obrigatório')
        # complete data and publish document
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-source/1', post_data)
        self.assertRedirects(response, '/bibliographic/')

        # test create new analytic
        post_data = form_data['Mamc']
        post_data.update(blank_formsets)
        response = self.client.post('/bibliographic/new-analytic?source=1', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')
        # check if record is on the list
        response = self.client.get('/bibliographic/analytics?source=1')
        self.assertContains(response, 'Primeira analítica')

        # test edit and publish analytic
        post_data['status'] = 1
        post_data.update(primary_descriptor)
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        # check validation of page or url
        self.assertContains(response, 'Endereço eletrônico, texto completo OU paginação obrigatório')
        # complete data and publish document
        post_data['electronic_address'] = '[{"_u": "http://fulltext.org", "_i": "pt", "_q": "pdf", "_y": "PDF" }]'
        response = self.client.post('/bibliographic/edit-analytic/2', post_data)
        self.assertRedirects(response, '/bibliographic/analytics?source=1')


class BiblioRefListGet(BaseTestCase):
    def setUp(self):
        super(BiblioRefListGet, self).setUp()
        self.login_documentalist()

    def test_get(self):
        """ Must return status code 200 """
        response = self.client.get("/bibliographic/")
        self.assertEqual(200, response.status_code)

    def test_template(self):
        """ Must use biblioref/reference_list.html template """
        response = self.client.get("/bibliographic/")
        self.assertTemplateUsed(response, "biblioref/reference_list.html")

    def test_search_by_status(self):
        """ Must return only references which have the selected status """
        baker.make("ReferenceSource", id=1)
        baker.make(
            "Reference", id=1, reference_title="Test Migration", status=-3,
            created_time="1970-01-01 00:00", literature_type="TEST"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_status": "-3", "filter_owner": "*"}
        ) # MIGRATION

        self.assertContains(response, '<a href="/bibliographic/edit-source/1">1</a>')

    def test_exclude_deleted_sources_from_results(self):
        """ Must exclude from the result list source references with deleted status """
        baker.make(
            "ReferenceSource", id=1, title_serial="Revista Test", reference_title="Test Source", status=3,
            created_time="1970-01-01 00:00", literature_type="S"
        )
        baker.make(
            "ReferenceAnalytic", source_id=1, title=[{'text': 'Test Analytic'}], status=3,
            created_time="1970-01-01 00:00", literature_type="S", treatment_level="as"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_owner": "*"}
        )

        self.assertContains(response, '<span class="badge badge-info">1</span>')

    def test_filter_owner_user(self):
        """ Default filter must show only current user's records """
        current_user = User.objects.get(username='doc')
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        baker.make(
            "ReferenceSource", reference_title="My Record", status=-1,
            created_by=current_user, created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )
        baker.make(
            "ReferenceSource", reference_title="Other Record", status=-1,
            created_by=other_user, created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )

        response = self.client.get("/bibliographic/")

        self.assertContains(response, "My Record")
        self.assertNotContains(response, "Other Record")

    def test_filter_owner_center(self):
        """ Filter by cooperative center must show only records from user's CC """
        baker.make(
            "ReferenceSource", reference_title="BR1.1 Record", status=-1,
            cooperative_center_code="BR1.1", created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )
        baker.make(
            "ReferenceSource", reference_title="PY3.1 Record", status=-1,
            cooperative_center_code="PY3.1", created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_owner": "center"}
        )

        self.assertContains(response, "BR1.1 Record")
        self.assertNotContains(response, "PY3.1 Record")

    def test_filter_owner_all(self):
        """ Filter owner=* must show all records """
        current_user = User.objects.get(username='doc')
        other_user = User.objects.create_user('other', 'other@test.com', 'other')

        baker.make(
            "ReferenceSource", reference_title="Record A", status=-1,
            created_by=current_user, created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )
        baker.make(
            "ReferenceSource", reference_title="Record B", status=-1,
            created_by=other_user, created_time="1970-01-01 00:00",
            literature_type="S", treatment_level="as"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_owner": "*"}
        )

        self.assertContains(response, "Record A")
        self.assertContains(response, "Record B")

    def test_filter_by_document_type(self):
        """ Must filter records by document type (literature_type + treatment_level) """
        baker.make(
            "ReferenceSource", reference_title="Serial Source", status=-1,
            literature_type="S", treatment_level="", title_serial="Revista X",
            volume_serial="1", issue_number="2", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="Monograph Source", status=-1,
            literature_type="M", treatment_level="m",
            title_monographic=[{"text": "Monograph Source", "_i": "en"}],
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/sources", {"document_type": "Mm", "filter_owner": "*"}
        )

        self.assertContains(response, "Monograph Source")
        self.assertNotContains(response, "Serial Source")

    def test_filter_by_analytic_document_type(self):
        """ Must filter analytic records by document type Sas """
        source = baker.make(
            "ReferenceSource", title_serial="Revista Test",
            volume_serial="1", issue_number="2", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00", literature_type="S"
        )
        baker.make(
            "ReferenceAnalytic", source=source, reference_title="Serial Analytic",
            title=[{"text": "Serial Analytic", "_i": "en"}],
            status=-1, literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/analytics", {"document_type": "Sas", "filter_owner": "*"}
        )

        self.assertContains(response, "Serial Analytic")

    def test_filter_status_draft(self):
        """ Must return only draft records and exclude serial sources """
        baker.make(
            "ReferenceSource", reference_title="Draft Analytic", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="Published Record", status=1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        # serial source with empty treatment_level should be excluded from draft filter
        baker.make(
            "ReferenceSource", reference_title="Draft Serial Source", status=-1,
            literature_type="S", treatment_level="",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_status": "-1", "filter_owner": "*"}
        )

        self.assertContains(response, "Draft Analytic")
        self.assertNotContains(response, "Published Record")
        self.assertNotContains(response, "Draft Serial Source")

    def test_filter_status_published(self):
        """ Must return only published records """
        baker.make(
            "ReferenceSource", reference_title="Published Record", status=1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="Draft Record", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_status": "1", "filter_owner": "*"}
        )

        self.assertContains(response, "Published Record")
        self.assertNotContains(response, "Draft Record")

    @override_settings(FULLTEXT_SEARCH=False)
    def test_search_by_title(self):
        """ Must return only records matching the search term """
        baker.make(
            "ReferenceSource", reference_title="Malaria Treatment Study", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="Dengue Prevention", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/", {"s": "Malaria", "filter_owner": "*"}
        )

        self.assertContains(response, "Malaria Treatment Study")
        self.assertNotContains(response, "Dengue Prevention")

    @override_settings(FULLTEXT_SEARCH=False)
    def test_search_by_field_id(self):
        """ Must return the exact record when searching by id field """
        ref = baker.make(
            "ReferenceSource", reference_title="Specific Record", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/", {"s": "id:{}".format(ref.id), "filter_owner": "*"}
        )

        self.assertContains(response, "Specific Record")

    def test_context_contains_expected_keys(self):
        """ Must include all expected keys in the template context """
        response = self.client.get("/bibliographic/")

        self.assertIn('actions', response.context)
        self.assertIn('document_type', response.context)
        self.assertIn('source_id', response.context)
        self.assertIn('user_data', response.context)
        self.assertIn('user_role', response.context)
        self.assertIn('indexed_database_list', response.context)
        self.assertIn('collection_list', response.context)

    def test_unauthenticated_user_redirected(self):
        """ Must redirect unauthenticated users to the login page """
        self.client.logout()

        response = self.client.get("/bibliographic/")

        self.assertEqual(302, response.status_code)

    def test_custom_ordering(self):
        """ Must order records by specified field in descending order """
        baker.make(
            "ReferenceSource", reference_title="Alpha Record", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="Zeta Record", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/",
            {"order": "-", "orderby": "reference_title", "filter_owner": "*"}
        )

        content = response.content.decode()
        pos_zeta = content.find("Zeta Record")
        pos_alpha = content.find("Alpha Record")
        self.assertTrue(pos_zeta < pos_alpha, "Zeta should appear before Alpha in descending order")

    def test_draft_filter_excludes_serial_sources(self):
        """ Draft filter must exclude sources with empty treatment_level """
        source = baker.make(
            "ReferenceSource", reference_title="Draft Source", status=-1,
            literature_type="S", treatment_level="",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceAnalytic", source=source, reference_title="Draft Analytic", status=-1,
            literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/", {"filter_status": "-1", "filter_owner": "*"}
        )

        self.assertNotContains(response, "Draft Source")
        self.assertContains(response, "Draft Analytic")


class BiblioRefSourceListGet(BaseTestCase):
    def setUp(self):
        super(BiblioRefSourceListGet, self).setUp()
        self.login_documentalist()

    def test_list_sources_view(self):
        """ Must return status code 200 for sources list """
        response = self.client.get("/bibliographic/sources")
        self.assertEqual(200, response.status_code)

    def test_editor_llxp_sources_filtered_by_center(self):
        """ LLXP editor must only see sources from their cooperative center """
        from django.core.cache import cache
        cache.clear()

        self.client.logout()
        self.login_editor_llxp()

        baker.make(
            "ReferenceSource", reference_title="BR772 Source", status=-1,
            cooperative_center_code="BR772", literature_type="S",
            treatment_level="", title_serial="Revista BR772",
            volume_serial="1", issue_number="1", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceSource", reference_title="BR1.1 Source", status=-1,
            cooperative_center_code="BR1.1", literature_type="S",
            treatment_level="", title_serial="Revista BR1.1",
            volume_serial="1", issue_number="1", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get("/bibliographic/sources")

        self.assertContains(response, "Revista BR772")
        self.assertNotContains(response, "Revista BR1.1")


class BiblioRefAnalyticListGet(BaseTestCase):
    def setUp(self):
        super(BiblioRefAnalyticListGet, self).setUp()
        self.login_documentalist()

    def test_list_analytics_view(self):
        """ Must return status code 200 for analytics list """
        source = baker.make(
            "ReferenceSource", title_serial="Revista Test",
            volume_serial="1", issue_number="2", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00", literature_type="S"
        )
        baker.make(
            "ReferenceAnalytic", source=source, reference_title="Test Analytic",
            title=[{"text": "Test Analytic", "_i": "en"}],
            status=-1, literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/analytics", {"source": source.id}
        )

        self.assertEqual(200, response.status_code)
        self.assertContains(response, "Test Analytic")

    def test_list_analytics_filtered_by_source(self):
        """ Must show only analytics from the specified source """
        source1 = baker.make(
            "ReferenceSource", title_serial="Revista A",
            volume_serial="1", issue_number="1", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00", literature_type="S"
        )
        source2 = baker.make(
            "ReferenceSource", title_serial="Revista B",
            volume_serial="2", issue_number="1", publication_date_normalized="20200101",
            created_time="1970-01-01 00:00", literature_type="S"
        )
        baker.make(
            "ReferenceAnalytic", source=source1, reference_title="Analytic From A",
            title=[{"text": "Analytic From A", "_i": "en"}],
            status=-1, literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )
        baker.make(
            "ReferenceAnalytic", source=source2, reference_title="Analytic From B",
            title=[{"text": "Analytic From B", "_i": "en"}],
            status=-1, literature_type="S", treatment_level="as",
            created_time="1970-01-01 00:00"
        )

        response = self.client.get(
            "/bibliographic/analytics", {"source": source1.id}
        )

        self.assertContains(response, "Analytic From A")
        self.assertNotContains(response, "Analytic From B")
