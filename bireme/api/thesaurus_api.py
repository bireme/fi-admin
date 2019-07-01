# coding: utf-8

'''
DESCRIPTORS

Chamada
http://fi-admin.beta.bvsalud.org/api/thesaurus/?format=json&ths=1&decs_code=23

'''

from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib.contenttypes.models import ContentType

from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from thesaurus.models import *
from isis_serializer import ISISSerializer

from tastypie_custom import CustomResource

from thesaurus.field_definitions_thesaurus import field_tag_map

import requests
import urllib
import json

from django.db.models import Q


class ThesaurusResource(CustomResource):
    class Meta:
        queryset = IdentifierDesc.objects.all()
        allowed_methods = ['get']
        serializer = ISISSerializer(formats=['json', 'xml', 'isis_id'], field_tag=field_tag_map)
        resource_name = 'thesaurus'
        filtering = {
            'update_date': ('gte', 'lte'),
            'status': 'exact',
            'id': ALL,
            'ths': ALL,
            'decs_code': ALL,
        }
        include_resource_uri = True



    def build_filters(self, filters=None):
        orm_filters = super(ThesaurusResource, self).build_filters(filters)

        # Escolhe obrigatoriamente o tesauro para uso. Caso não seja escolhido não renderiza
        if 'ths' in filters:
            filter_ths = filters['ths']
            orm_filters['thesaurus_id__exact'] = filter_ths
        else:
            orm_filters['thesaurus_id__exact'] = ''

        return orm_filters



    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_search'), name="api_get_search"),
        ]



    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        q = request.GET.get('q', '')
        fq = request.GET.get('fq', '')
        start = request.GET.get('start', '')
        count = request.GET.get('count', '')
        lang = request.GET.get('lang', 'pt')
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'created_date desc')
        decs_code = request.GET.get('decs_code', '')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:title.title*) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:title.title*)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main', 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort, 'decs_code': decs_code }

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())



    def dehydrate(self, bundle):

        id = IdentifierDesc.objects.filter(id=bundle.obj.id).values('id')
        for field in id:
            # bundle.data['id'] = str(bundle.obj.id)
            identifier_id = bundle.obj.id


        # IdentifierDesc
        array_fields = {}
        array_fields_all = []
        abbreviation_arr = []

        array_fields_abbreviation = {}
        array_fields_abbreviation_all = []
        results = IdentifierDesc.objects.filter(id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["thesaurus"] = field.thesaurus
            array_fields["descriptor_class"] = field.descriptor_class
            array_fields["descriptor_ui"] = field.descriptor_ui
            array_fields["decs_code"] = field.decs_code
            array_fields["external_code"] = field.external_code
            array_fields["nlm_class_number"] = field.nlm_class_number
            array_fields["date_created"] = field.date_created
            array_fields["date_revised"] = field.date_revised
            array_fields["date_established"] = field.date_established
        
            id_abbrev = IdentifierDesc.objects.filter(id=field.id).values('abbreviation')
            allowed_qualifiers = IdentifierQualif.objects.filter(id__in=id_abbrev).order_by('abbreviation')
            allowed_qualifiers_concat = ''
            for field in allowed_qualifiers:
                array_fields_abbreviation["id"] = field.id
                array_fields_abbreviation["abbreviation"] = field.abbreviation

                # Proporciona o campo term_string nos idiomas existentes
                abbreviation_fields_language = {}
                abbreviation_language_all = []
                concepts_of_register = IdentifierConceptListQualif.objects.filter(identifier_id=field.id,preferred_concept='Y').values('id')
                id_concept = concepts_of_register[0].get('id')
                terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept,concept_preferred_term='Y',record_preferred_term='Y')
                for term in terms_of_concept:
                    abbreviation_fields_language['term_string'] = term.term_string.encode('utf-8')
                    abbreviation_fields_language['language_code'] = term.language_code

                    # Armazena array
                    abbreviation_language_all.append(abbreviation_fields_language)

                    # Zera array pra próxima leitura
                    abbreviation_fields_language = {}

                array_fields_abbreviation["term_string_translations"] = abbreviation_language_all

                # Armazena array
                array_fields_abbreviation_all.append(array_fields_abbreviation)

                # Zera array pra próxima leitura
                array_fields_abbreviation = {}

            # Cria array de abreviações
            array_fields["Abbreviations"] = array_fields_abbreviation_all


            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['IdentifierDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # DescriptionDesc
        array_fields = {}
        array_fields_all = []
        results = DescriptionDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["language_code"] = field.language_code
            array_fields["annotation"] = field.annotation
            array_fields["history_note"] = field.history_note
            array_fields["online_note"] = field.online_note
            array_fields["public_mesh_note"] = field.public_mesh_note
            array_fields["consider_also"] = field.consider_also

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['DescriptionDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # TreeNumbersListDesc
        array_fields = {}
        array_fields_all = []
        results = TreeNumbersListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["tree_number"] = field.tree_number

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['TreeNumbersListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # PharmacologicalActionList
        array_fields = {}
        array_fields_all = []
        results = PharmacologicalActionList.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["term_string"] = field.term_string
            array_fields["descriptor_ui"] = field.descriptor_ui
            array_fields["language_code"] = field.language_code

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['PharmacologicalActionList'] = array_fields_all

        # =========================================================================================================================================================================

        # Tavlez deverá ser criado um preenchimento para todos os idiomas existentes
        # Fazer uma consulta pelo descriptor_ui e trazer o term_string em n idiomas
        # SeeRelatedListDesc
        array_fields = {}
        array_fields_all = []
        results = SeeRelatedListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["term_string"] = field.term_string
            array_fields["descriptor_ui"] = field.descriptor_ui

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['SeeRelatedListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # PreviousIndexingListDesc
        array_fields = {}
        array_fields_all = []
        results = PreviousIndexingListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["previous_indexing"] = field.previous_indexing
            array_fields["language_code"] = field.language_code

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['PreviousIndexingListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # EntryCombinationListDesc
        array_fields = {}
        array_fields_all = []
        results = EntryCombinationListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["ecin_qualif"] = field.ecin_qualif
            array_fields["ecin_id"] = field.ecin_id

            array_fields["ecout_desc"] = field.ecout_desc
            array_fields["ecout_desc_id"] = field.ecout_desc_id
            array_fields["ecout_qualif"] = field.ecout_qualif
            array_fields["ecout_qualif_id"] = field.ecout_qualif_id
            
            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['EntryCombinationListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # IdentifierConceptListDesc
        array_fields = {}
        array_fields_all = []
        results = IdentifierConceptListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            identifier_concept_id = field.id
            array_fields["concept_ui"] = field.concept_ui
            array_fields["concept_relation_name"] = field.concept_relation_name
            array_fields["preferred_concept"] = field.preferred_concept
            array_fields["casn1_name"] = field.casn1_name
            array_fields["registry_number"] = field.registry_number
            array_fields["historical_annotation"] = field.historical_annotation

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer desxcrição dos conceitos
            array_fields_ConceptListDesc = {}
            ConceptListDesc_results = ConceptListDesc.objects.filter(identifier_concept_id=identifier_concept_id)
            for field in ConceptListDesc_results:
                # Armazena campos
                array_fields_ConceptListDesc["id"] = field.id
                array_fields_ConceptListDesc["language_code"] = field.language_code
                array_fields_ConceptListDesc["scope_note"] = field.scope_note

            array_fields["ConceptListDesc"] = array_fields_ConceptListDesc

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer os termos do conceito
            array_fields_TermListDesc = {}
            array_fields_TermListDesc_all = []
            TermListDesc_results = TermListDesc.objects.filter(identifier_concept_id=identifier_concept_id)
            for field in TermListDesc_results:
                # Armazena campos
                if field.status == 1:
                    array_fields_TermListDesc["id"] = field.id
                    identifier_term_id = field.id
                    array_fields_TermListDesc["status"] = field.status
                    array_fields_TermListDesc["term_ui"] = field.term_ui
                    array_fields_TermListDesc["language_code"] = field.language_code
                    array_fields_TermListDesc["term_string"] = field.term_string
                    array_fields_TermListDesc["concept_preferred_term"] = field.concept_preferred_term
                    array_fields_TermListDesc["is_permuted_term"] = field.is_permuted_term
                    array_fields_TermListDesc["lexical_tag"] = field.lexical_tag
                    array_fields_TermListDesc["record_preferred_term"] = field.record_preferred_term
                    array_fields_TermListDesc["entry_version"] = field.entry_version
                    array_fields_TermListDesc["date_created"] = field.date_created
                    array_fields_TermListDesc["date_altered"] = field.date_altered
                    array_fields_TermListDesc["historical_annotation"] = field.historical_annotation
                    array_fields_TermListDesc["term_thesaurus"] = field.term_thesaurus

                    # =========================================================================================================================================================================
                    # Faz pesquisa para trazer tesauro que ocorre
                    array_fields_TheraurusOccurrenceListDesc = {}
                    array_fields_TheraurusOccurrenceListDesc_all = []
                    TheraurusOccurrenceListDesc_results = TheraurusOccurrenceListDesc.objects.filter(identifier_term_id=identifier_term_id)
                    for field in TheraurusOccurrenceListDesc_results:
                        # Armazena campos
                        array_fields_TheraurusOccurrenceListDesc["id"] = field.id
                        array_fields_TheraurusOccurrenceListDesc["thesaurus_occurrence"] = field.thesaurus_occurrence

                        # Armazena array
                        array_fields_TheraurusOccurrenceListDesc_all.append(array_fields_TheraurusOccurrenceListDesc)
                        array_fields_TheraurusOccurrenceListDesc = {}

                    array_fields_TermListDesc["TheraurusOccurrenceListDesc"] = array_fields_TheraurusOccurrenceListDesc_all


                    # Armazena array
                    array_fields_TermListDesc_all.append(array_fields_TermListDesc)
                    array_fields_TermListDesc = {}

            array_fields["TermListDesc"] = array_fields_TermListDesc_all


            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['IdentifierConceptListDesc'] = array_fields_all



















        return bundle
