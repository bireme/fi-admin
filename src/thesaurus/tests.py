#-*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test.client import Client

from .models import *
from utils.tests import BaseTestCase


def create_thesaurus():
    """
    Create a Thesaurus object for tests
    """
    return Thesaurus.objects.create(
        thesaurus_name='DeCS',
        thesaurus_author='BIREME',
        thesaurus_scope='DeCS',
        thesaurus_acronym='DEC',
    )


def minimal_form_data_descriptor(thesaurus_id):
    """
    Minimum fields to submit the Descriptor Step 1 form (IdentifierDescForm + formsets)
    """
    form_data = {
        'thesaurus': str(thesaurus_id),

        # DescriptionDesc formset (related_name: descriptiondesc)
        'descriptiondesc-TOTAL_FORMS': '0',
        'descriptiondesc-INITIAL_FORMS': '0',

        # TreeNumbersListDesc formset (related_name: dtreenumbers) — at least 1 required
        'dtreenumbers-TOTAL_FORMS': '1',
        'dtreenumbers-INITIAL_FORMS': '0',
        'dtreenumbers-0-tree_number': 'A01',

        # PharmacologicalActionList formset (related_name: pharmacodesc)
        'pharmacodesc-TOTAL_FORMS': '0',
        'pharmacodesc-INITIAL_FORMS': '0',

        # SeeRelatedListDesc formset (related_name: relateddesc)
        'relateddesc-TOTAL_FORMS': '0',
        'relateddesc-INITIAL_FORMS': '0',

        # PreviousIndexingListDesc formset (related_name: previousdesc)
        'previousdesc-TOTAL_FORMS': '0',
        'previousdesc-INITIAL_FORMS': '0',

        # EntryCombinationListDesc formset (related_name: entrycombinationlistdesc)
        'entrycombinationlistdesc-TOTAL_FORMS': '0',
        'entrycombinationlistdesc-INITIAL_FORMS': '0',
    }

    return form_data


def minimal_form_data_qualifier(thesaurus_id):
    """
    Minimum fields to submit the Qualifier Step 1 form (IdentifierQualifForm + formsets)
    """
    form_data = {
        'thesaurus': str(thesaurus_id),
        'abbreviation': 'AA',

        # DescriptionQualif formset (related_name: descriptionqualif)
        'descriptionqualif-TOTAL_FORMS': '0',
        'descriptionqualif-INITIAL_FORMS': '0',

        # TreeNumbersListQualif formset (related_name: qtreenumbers) — at least 1 required
        'qtreenumbers-TOTAL_FORMS': '1',
        'qtreenumbers-INITIAL_FORMS': '0',
        'qtreenumbers-0-tree_number': 'Q01',
    }

    return form_data


def create_descriptor_with_term(thesaurus, user):
    """
    Create a full Descriptor chain via ORM: IdentifierDesc → IdentifierConceptListDesc → TermListDesc
    """
    identifier = IdentifierDesc.objects.create(
        thesaurus=thesaurus,
        created_by=user,
    )

    concept = IdentifierConceptListDesc.objects.create(
        identifier=identifier,
        preferred_concept='Y',
    )

    term = TermListDesc.objects.create(
        identifier_concept=concept,
        term_string='Malaria',
        language_code='en',
        status=1,
        concept_preferred_term='Y',
        record_preferred_term='Y',
        term_thesaurus=str(thesaurus.id),
    )

    return identifier, concept, term


def create_qualifier_with_term(thesaurus, user):
    """
    Create a full Qualifier chain via ORM: IdentifierQualif → IdentifierConceptListQualif → TermListQualif
    """
    qualifier = IdentifierQualif.objects.create(
        thesaurus=thesaurus,
        abbreviation='AB',
        created_by=user,
    )

    concept = IdentifierConceptListQualif.objects.create(
        identifier=qualifier,
        preferred_concept='Y',
    )

    term = TermListQualif.objects.create(
        identifier_concept=concept,
        term_string='diagnosis',
        language_code='en',
        status=1,
        concept_preferred_term='Y',
        record_preferred_term='Y',
        term_thesaurus=str(thesaurus.id),
    )

    return qualifier, concept, term


class DescriptorTest(BaseTestCase):
    """
    Tests for thesaurus descriptor CRUD
    """

    def setUp(self):
        super(DescriptorTest, self).setUp()
        self.thesaurus = create_thesaurus()

    def test_list_descriptor(self):
        """
        Test list descriptors — list view shows TermListDesc objects
        """
        user = self.login_admin()
        identifier, concept, term = create_descriptor_with_term(self.thesaurus, user)

        response = self.client.get('/thesaurus/descriptors/', {
            'choiced_thesaurus': str(self.thesaurus.id),
            'visited': 'ok',
        })
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Malaria')

    def test_add_descriptor(self):
        """
        Tests create descriptor (Step 1) — should redirect to concept+term creation (Step 2)
        """
        self.login_admin()

        form_data = minimal_form_data_descriptor(self.thesaurus.id)
        url = '/thesaurus/descriptors/new?ths={0}&language_code=en&term=test'.format(
            self.thesaurus.id)

        response = self.client.post(url, form_data, follow=True)

        # Step 1 creates IdentifierDesc and redirects to Step 2 (concept+term)
        self.assertEqual(200, response.status_code)
        self.assertEqual(IdentifierDesc.objects.count(), 1)

        # Verify auto-generated fields
        desc = IdentifierDesc.objects.first()
        self.assertTrue(desc.decs_code)
        self.assertTrue(desc.descriptor_ui)
        self.assertIn('DEC', desc.descriptor_ui)

    def test_edit_descriptor(self):
        """
        Tests edit descriptor register
        """
        user = self.login_admin()
        identifier, concept, term = create_descriptor_with_term(self.thesaurus, user)

        # Create a tree number for the identifier (required for edit form_valid)
        TreeNumbersListDesc.objects.create(
            identifier=identifier,
            tree_number='B01',
        )

        base_url = '/thesaurus/descriptors/register/edit/{0}'.format(identifier.id)
        url = '{0}?ths={1}'.format(base_url, self.thesaurus.id)

        # Test GET returns the edit form
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # Test POST with updated data — need at least 1 description entry
        # (form_valid accesses formset_descriptor.cleaned_data[0])
        form_data = minimal_form_data_descriptor(self.thesaurus.id)
        form_data['descriptiondesc-TOTAL_FORMS'] = '1'
        form_data['descriptiondesc-0-language_code'] = 'en'
        form_data['descriptiondesc-0-identifier'] = str(identifier.id)
        form_data['dtreenumbers-TOTAL_FORMS'] = '1'
        form_data['dtreenumbers-INITIAL_FORMS'] = '1'
        form_data['dtreenumbers-0-id'] = str(TreeNumbersListDesc.objects.first().id)
        form_data['dtreenumbers-0-identifier'] = str(identifier.id)
        form_data['dtreenumbers-0-tree_number'] = 'B01'
        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(200, response.status_code)

    def test_delete_descriptor(self):
        """
        Tests delete descriptor
        """
        user = self.login_admin()
        # Create bare identifier (no PROTECT-related objects)
        identifier = IdentifierDesc.objects.create(
            thesaurus=self.thesaurus,
            created_by=user,
        )

        url = '/thesaurus/descriptors/delete/{0}?ths={1}'.format(
            identifier.id, self.thesaurus.id)

        # Test GET shows confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Você tem certeza que deseja apagar?")

        # Test POST deletes the record
        response = self.client.post(url)
        self.assertEqual(IdentifierDesc.objects.filter(id=identifier.id).count(), 0)
        self.assertRedirects(response,
                             '/thesaurus/descriptors/?ths={0}'.format(self.thesaurus.id))


class QualifierTest(BaseTestCase):
    """
    Tests for thesaurus qualifier CRUD
    """

    def setUp(self):
        super(QualifierTest, self).setUp()
        self.thesaurus = create_thesaurus()

    def test_list_qualifier(self):
        """
        Test list qualifiers — list view shows TermListQualif objects
        """
        user = self.login_admin()
        qualifier, concept, term = create_qualifier_with_term(self.thesaurus, user)

        response = self.client.get('/thesaurus/qualifiers/', {
            'choiced_thesaurus': str(self.thesaurus.id),
            'visited': 'ok',
        })
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'diagnosis')

    def test_add_qualifier(self):
        """
        Tests create qualifier (Step 1) — should redirect to concept+term creation (Step 2)
        """
        self.login_admin()

        form_data = minimal_form_data_qualifier(self.thesaurus.id)
        url = '/thesaurus/qualifiers/new?ths={0}&language_code=en&term=test'.format(
            self.thesaurus.id)

        response = self.client.post(url, form_data, follow=True)

        # Step 1 creates IdentifierQualif and redirects to Step 2
        self.assertEqual(200, response.status_code)
        self.assertEqual(IdentifierQualif.objects.count(), 1)

        # Verify auto-generated fields
        qualif = IdentifierQualif.objects.first()
        self.assertTrue(qualif.decs_code)
        self.assertTrue(qualif.qualifier_ui)
        self.assertIn('DEC', qualif.qualifier_ui)

    def test_edit_qualifier(self):
        """
        Tests edit qualifier register
        """
        user = self.login_admin()
        qualifier, concept, term = create_qualifier_with_term(self.thesaurus, user)

        # Create a tree number for the qualifier (required for edit form_valid)
        TreeNumbersListQualif.objects.create(
            identifier=qualifier,
            tree_number='Q01',
        )

        url = '/thesaurus/qualifiers/register/edit/{0}?ths={1}'.format(
            qualifier.id, self.thesaurus.id)

        # Test GET returns the form
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # Test POST with updated data — need at least 1 description entry
        # (form_valid accesses formset_descriptor.cleaned_data[0])
        form_data = minimal_form_data_qualifier(self.thesaurus.id)
        form_data['descriptionqualif-TOTAL_FORMS'] = '1'
        form_data['descriptionqualif-0-language_code'] = 'en'
        form_data['descriptionqualif-0-identifier'] = str(qualifier.id)
        form_data['qtreenumbers-TOTAL_FORMS'] = '1'
        form_data['qtreenumbers-INITIAL_FORMS'] = '1'
        form_data['qtreenumbers-0-id'] = str(TreeNumbersListQualif.objects.first().id)
        form_data['qtreenumbers-0-identifier'] = str(qualifier.id)
        form_data['qtreenumbers-0-tree_number'] = 'Q01'

        response = self.client.post(url, form_data, follow=True)
        self.assertEqual(200, response.status_code)

    def test_delete_qualifier(self):
        """
        Tests delete qualifier
        """
        user = self.login_admin()
        # Create bare qualifier (no PROTECT-related objects)
        qualifier = IdentifierQualif.objects.create(
            thesaurus=self.thesaurus,
            abbreviation='ZZ',
            created_by=user,
        )

        url = '/thesaurus/qualifiers/delete/{0}?ths={1}'.format(
            qualifier.id, self.thesaurus.id)

        # Test GET shows confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Você tem certeza que deseja apagar?")

        # Test POST deletes the record
        response = self.client.post(url)
        self.assertEqual(IdentifierQualif.objects.filter(id=qualifier.id).count(), 0)
        self.assertRedirects(response,
                             '/thesaurus/qualifiers/?ths={0}'.format(self.thesaurus.id))


class DescriptorSearchTest(BaseTestCase):
    """
    Tests search for descriptors by term string
    """

    def test_search_term(self):
        self.login_admin()
        thesaurus = create_thesaurus()

        # Create two descriptors with different term strings
        id1 = IdentifierDesc.objects.create(thesaurus=thesaurus)
        c1 = IdentifierConceptListDesc.objects.create(identifier=id1, preferred_concept='Y')
        TermListDesc.objects.create(
            identifier_concept=c1, term_string='Malaria', language_code='en',
            status=1, concept_preferred_term='Y', record_preferred_term='Y',
            term_thesaurus=str(thesaurus.id),
        )

        id2 = IdentifierDesc.objects.create(thesaurus=thesaurus)
        c2 = IdentifierConceptListDesc.objects.create(identifier=id2, preferred_concept='Y')
        TermListDesc.objects.create(
            identifier_concept=c2, term_string='Dengue', language_code='en',
            status=1, concept_preferred_term='Y', record_preferred_term='Y',
            term_thesaurus=str(thesaurus.id),
        )

        response = self.client.get('/thesaurus/descriptors/', {
            'choiced_thesaurus': str(thesaurus.id),
            'visited': 'ok',
            's': 'Malaria',
        })
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Malaria')
        self.assertNotContains(response, 'Dengue')
