# coding: utf-8

from django.test.client import Client
from django.contrib.contenttypes.models import ContentType

from main.models import Descriptor, ResourceThematic, ThematicArea
from title.models import Title
from utils.models import AuxCode
from database.models import Database

from utils.tests import BaseTestCase
from models import *

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
