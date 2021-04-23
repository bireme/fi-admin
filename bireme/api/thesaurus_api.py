# coding: utf-8


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
import operator

from django.db.models import Q



class ThesaurusAPIDescResource(CustomResource):
    class Meta:
        queryset = IdentifierDesc.objects.using('decs_portal').all()
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
        orm_filters = super(ThesaurusAPIDescResource, self).build_filters(filters)

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

        # # filter result by approved resources (status=1)
        # if fq != '':
        #     fq = 'django_ct:thesaurus.identifierdesc* AND %s' % fq
        # else:
        #     fq = 'django_ct:thesaurus.identifierdesc*'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        # print 'search_url -->',search_url
        # print 'q          -->',q

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort, 'decs_code': decs_code }

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def dehydrate(self, bundle):

        id = IdentifierDesc.objects.using('decs_portal').filter(id=bundle.obj.id).values('id')
        for field in id:
            identifier_id = bundle.obj.id

        # IdentifierDesc
        array_fields = {}
        array_fields_all = []
        abbreviation_arr = []

        array_fields_abbreviation = {}
        array_fields_abbreviation_all = []
        results = IdentifierDesc.objects.using('decs_portal').filter(id=identifier_id)
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

            id_abbrev = IdentifierDesc.objects.using('decs_portal').filter(id=field.id).values('abbreviation')
            allowed_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(id__in=id_abbrev).order_by('abbreviation')
            allowed_qualifiers_concat = ''
            for field in allowed_qualifiers:
                array_fields_abbreviation["id"] = field.id
                array_fields_abbreviation["decs_code"] = field.decs_code
                array_fields_abbreviation["abbreviation"] = field.abbreviation

                # Proporciona o campo term_string nos idiomas existentes
                abbreviation_fields_language = {}
                abbreviation_language_all = []
                concepts_of_register = IdentifierConceptListQualif.objects.using('decs_portal').filter(identifier_id=field.id,preferred_concept='Y').values('id')
                id_concept = concepts_of_register[0].get('id')
                terms_of_concept = TermListQualif.objects.using('decs_portal').filter(identifier_concept_id=id_concept,concept_preferred_term='Y',record_preferred_term='Y')
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
        results = DescriptionDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
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
        results = TreeNumbersListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
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
        results = PharmacologicalActionList.objects.using('decs_portal').filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            if field.term_string:
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
        results = SeeRelatedListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
        for field in results:
            descriptor_ui = field.descriptor_ui
            id_register = IdentifierDesc.objects.using('decs_portal').filter(descriptor_ui=descriptor_ui).values('id')

            array_fields['descriptor_ui'] = field.descriptor_ui

            IdentifierDesc_decs_code = IdentifierDesc.objects.using('decs_portal').filter(descriptor_ui=field.descriptor_ui).values('decs_code')
            array_fields['decs_code'] = IdentifierDesc_decs_code[0].get('decs_code')

            concepts_of_register = IdentifierConceptListDesc.objects.using('decs_portal').filter(identifier_id=id_register,preferred_concept='Y').values('id')
            id_concept = concepts_of_register[0].get('id')
            terms_of_concept = TermListDesc.objects.using('decs_portal').filter(identifier_concept_id=id_concept,concept_preferred_term='Y',record_preferred_term='Y',status=1)

            array_terms = {}
            array_terms_all = []
            for term in terms_of_concept:
                array_terms['term_string'] = term.term_string.encode('utf-8')
                array_terms['language_code'] = term.language_code
                # Armazena array
                array_terms_all.append(array_terms)
                array_terms = {}

            array_fields['terms'] = array_terms_all

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['SeeRelatedListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # PreviousIndexingListDesc
        array_fields = {}
        array_fields_all = []
        results = PreviousIndexingListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
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
        results = EntryCombinationListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
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
        results = IdentifierConceptListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
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
            # Faz pesquisa para trazer descrição dos conceitos
            array_fields_ConceptListDesc = {}
            array_fields_ConceptListDesc_all = []
            ConceptListDesc_results = ConceptListDesc.objects.using('decs_portal').filter(identifier_concept_id=identifier_concept_id)
            for field in ConceptListDesc_results:

                if field.language_code and field.scope_note:
                    # Armazena campos
                    array_fields_ConceptListDesc["id"] = field.id
                    array_fields_ConceptListDesc["language_code"] = field.language_code
                    array_fields_ConceptListDesc["scope_note"] = field.scope_note

                    array_fields_ConceptListDesc_all.append(array_fields_ConceptListDesc)
                    array_fields_ConceptListDesc = {}

            array_fields["ConceptListDesc"] = array_fields_ConceptListDesc_all

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer os termos do conceito
            array_fields_TermListDesc = {}
            array_fields_TermListDesc_all = []
            TermListDesc_results = TermListDesc.objects.using('decs_portal').filter(identifier_concept_id=identifier_concept_id)
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
                    TheraurusOccurrenceListDesc_results = TheraurusOccurrenceListDesc.objects.using('decs_portal').filter(identifier_term_id=identifier_term_id)
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


        # =========================================================================================================================================================================
        # Prepara insumo para geração da Árvore hierárquica
        # HierarchicalTree
        # ----------------

        array_fields = {}
        array_fields_all = []

        thesaurus_choiced = IdentifierDesc.objects.using('decs_portal').filter(id=identifier_id).values('thesaurus_id')
        thesarus_choiced_id=thesaurus_choiced[0]['thesaurus_id']

        def SearchTermsforTreenumber(tree_number,leaf):

            # Encontra o descritor desse tree_number
            id_tree_number = TreeNumbersListDesc.objects.using('decs_portal').filter(tree_number=tree_number).values('identifier_id')
            id_concept = IdentifierConceptListDesc.objects.using('decs_portal').filter(identifier_id__in=id_tree_number,preferred_concept='Y').distinct().values('id')

            # status = 1
            q_status = Q(status=1)

            # concept_preferred_term='Y'
            q_concept_preferred_term = Q(concept_preferred_term='Y')

            # record_preferred_term='Y'
            q_record_preferred_term = Q(record_preferred_term='Y')

            q_id_concept = Q(identifier_concept_id__in=id_concept)

            terms_of_treenumber = TermListDesc.objects.using('decs_portal').filter( q_status & q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=thesarus_choiced_id)

            # Proporciona o campo term_string nos idiomas existentes
            treenumber_terms_language = {}
            treenumber_terms_language_all = []
            for term in terms_of_treenumber:

                treenumber_terms_language['term_string'] = term.term_string.encode('utf-8')
                treenumber_terms_language['language_code'] = term.language_code

                # Armazena array
                treenumber_terms_language_all.append(treenumber_terms_language)

                # Zera array pra próxima leitura
                treenumber_terms_language = {}

            array_fields["term_string_translations"] = treenumber_terms_language_all

            # Verifica se existem descendentes
            if leaf == True:
                leafs = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__tree_number__contains=tree_number).exclude(dtreenumbers__tree_number=tree_number)
                if leafs:
                    array_fields['leaf'] = True

            # Verifica o nivel que esta
            tponto = 1
            for letra in tree_number:
                if letra == '.':
                    tponto = tponto + 1

            array_fields['level'] = tponto

            # Descobre o decs_code do tree_number parent
            decs_code_results = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__tree_number=tree_number).values('decs_code')
            if decs_code_results:
                for field in decs_code_results:
                    array_fields["id"] = field.get('decs_code')



        # results = TreeNumbersListDesc.objects.using('decs_portal').filter(identifier_id=identifier_id)
        results = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__identifier_id=identifier_id).values('decs_code','dtreenumbers__tree_number')


        for field in results:
            # Armazena campos
            tree_number = field.get('dtreenumbers__tree_number')
            decs_code = field.get('decs_code')

            # Armazena primeira ocorrência
            array_fields["tipo"] = "primeira_ocorrencia"
            array_fields["tree_number"] = tree_number
            array_fields["tree_number_original"] = tree_number
            array_fields["id"] = decs_code

            # Armazena informação se é tree_number do registro
            tree_number_registry = tree_number
            if tree_number_registry:
                array_fields["tree_number_registry"] = True

            array_fields_all.append(array_fields)

            # Armazena demais ocorrências se houverem
            leaf=True
            SearchTermsforTreenumber(tree_number,leaf)

            array_fields = {}

            # Armazena ancestrais
            tam_tree_number = len(tree_number)
            while ( tam_tree_number>4 ):
                dif=tam_tree_number-4
                ancestor_tree_number=tree_number[0:dif]

                array_fields["tipo"] = "ancestral"
                array_fields["tree_number"] = ancestor_tree_number
                array_fields["tree_number_original"] = tree_number

                leaf=False
                SearchTermsforTreenumber(ancestor_tree_number,leaf)

                array_fields_all.append(array_fields)

                # Atualiza tamanho do tree_number
                tam_tree_number=len(ancestor_tree_number)

                # Zera array pra próxima leitura
                array_fields = {}


        # Armazena irmãos
        array_fields = {}
        array_fields_all_brothers = []
        for field in results:
            # Armazena campos
            tree_number = field.get('dtreenumbers__tree_number')
            decs_code = field.get('decs_code')

            tam_tree_number=len(tree_number)

            if tam_tree_number>4:
                dif=tam_tree_number-4
                ancestor_tree_number=tree_number[0:dif]

                # Pesquisa somente tree_number que tem o mesmo radical
                result_treenumbers_like = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__tree_number__contains=ancestor_tree_number).exclude(dtreenumbers__tree_number=tree_number).values('dtreenumbers__tree_number')

                if result_treenumbers_like:
                    for field in result_treenumbers_like:
                        read_treenumber=len(field.get('dtreenumbers__tree_number'))
                        if tam_tree_number == read_treenumber:
                            # Armazena o tree_number que tem o mesmo tamanho do tree_number do registro
                            array_fields["tipo"] = "irmão"
                            array_fields["tree_number"] = field.get('dtreenumbers__tree_number')
                            array_fields["tree_number_original"] = tree_number

                            # Armazena demais ocorrências se houverem
                            leaf=True
                            SearchTermsforTreenumber(field.get('dtreenumbers__tree_number'),leaf)

                            array_fields_all_brothers.append(array_fields)

                        # Zera array pra próxima leitura
                        array_fields = {}

        # Concatena array_fields_all_brothers
        array_fields_all.extend(array_fields_all_brothers)

        array_fields_all_brothers = []


        # # Armazena irmãos ancestrais
        # array_fields = {}
        # array_fields_all_brothers_ancestors = []
        # for field in results:
        #     # Armazena campos
        #     tree_number = field.get('dtreenumbers__tree_number')
        #     decs_code = field.get('decs_code')

        #     tam_tree_number=len(tree_number)

        #     if tam_tree_number>8:
        #         dif=tam_tree_number-8
        #         ancestor_tree_number=tree_number[0:dif]

        #         # tree_number que deverá ser desconsiderado
        #         dif=tam_tree_number-4
        #         ancestor_tree_number_exclude=tree_number[0:dif]

        #         # Pesquisa somente tree_number que tem o mesmo radical
        #         result_treenumbers_like = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__tree_number__contains=ancestor_tree_number).exclude(dtreenumbers__tree_number=ancestor_tree_number_exclude).values('dtreenumbers__tree_number')

        #         if result_treenumbers_like:
        #             for field in result_treenumbers_like:
        #                 read_treenumber=len(field.get('dtreenumbers__tree_number'))
        #                 tree_number_ancestral = field.get('dtreenumbers__tree_number')
        #                 if (tam_tree_number-4) == read_treenumber:
        #                     # Armazena o tree_number que tem o mesmo tamanho do tree_number do registro
        #                     array_fields["tipo"] = "irmão ancestral"
        #                     array_fields["tree_number"] = tree_number_ancestral
        #                     array_fields["tree_number_original"] = tree_number

        #                     # Armazena demais ocorrências se houverem
        #                     SearchTermsforTreenumber(tree_number_ancestral)

        #                     array_fields_all_brothers_ancestors.append(array_fields)

        #                 # Zera array pra próxima leitura
        #                 array_fields = {}

        #     # Concatena array_fields_all_brothers_ancestors
        #     array_fields_all.extend(array_fields_all_brothers_ancestors)

        #     array_fields_all_brothers_ancestors = []


        # Armazena filhos
        array_fields = {}
        array_fields_all_children = []
        for field in results:
            # Armazena campos
            tree_number = field.get('dtreenumbers__tree_number')
            decs_code = field.get('decs_code')

            tam_tree_number_children=len(tree_number)+4

            # Pesquisa somente tree_number que tem o mesmo radical
            result_treenumbers_like = IdentifierDesc.objects.using('decs_portal').filter(thesaurus_id=thesarus_choiced_id,dtreenumbers__tree_number__contains=tree_number).exclude(dtreenumbers__tree_number=tree_number).values('dtreenumbers__tree_number')

            if result_treenumbers_like:
                for field in result_treenumbers_like:
                    read_treenumber=len(field.get('dtreenumbers__tree_number'))
                    if tam_tree_number_children == read_treenumber:
                        # Armazena o tree_number que tem o mesmo tamanho do tree_number do registro
                        array_fields["tipo"] = "filho"
                        array_fields["tree_number"] = field.get('dtreenumbers__tree_number')
                        array_fields["tree_number_original"] = tree_number

                        # Armazena demais ocorrências se houverem
                        leaf=True
                        SearchTermsforTreenumber(field.get('dtreenumbers__tree_number'),leaf)

                        array_fields_all_children.append(array_fields)

                    # Zera array pra próxima leitura
                    array_fields = {}

        # Concatena array_fields_all_children
        array_fields_all.extend(array_fields_all_children)

        array_fields_all_children = []


        bundle.data['HierarchicalTree'] = array_fields_all

        return bundle



class ThesaurusAPIQualifResource(CustomResource):
    class Meta:
        queryset = IdentifierQualif.objects.using('decs_portal').all()
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
        orm_filters = super(ThesaurusAPIQualifResource, self).build_filters(filters)

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

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort, 'decs_code': decs_code }

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def dehydrate(self, bundle):

        id = IdentifierQualif.objects.using('decs_portal').filter(id=bundle.obj.id).values('id')
        for field in id:
            # bundle.data['id'] = str(bundle.obj.id)
            identifier_id = bundle.obj.id

        # IdentifierQualif
        array_fields = {}
        array_fields_all = []
        abbreviation_arr = []

        array_fields_abbreviation = {}
        array_fields_abbreviation_all = []
        results = IdentifierQualif.objects.using('decs_portal').filter(id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["thesaurus"] = field.thesaurus
            array_fields["qualifier_ui"] = field.qualifier_ui
            array_fields["decs_code"] = field.decs_code
            array_fields["external_code"] = field.external_code
            array_fields["date_created"] = field.date_created
            array_fields["date_revised"] = field.date_revised
            array_fields["date_established"] = field.date_established

            id_abbrev = IdentifierQualif.objects.using('decs_portal').filter(id=field.id).values('abbreviation')
            allowed_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(id__in=id_abbrev).order_by('abbreviation')
            allowed_qualifiers_concat = ''
            for field in allowed_qualifiers:
                array_fields_abbreviation["id"] = field.id
                array_fields_abbreviation["abbreviation"] = field.abbreviation

                # Proporciona o campo term_string nos idiomas existentes
                abbreviation_fields_language = {}
                abbreviation_language_all = []
                concepts_of_register = IdentifierConceptListQualif.objects.using('decs_portal').filter(identifier_id=field.id,preferred_concept='Y').values('id')
                id_concept = concepts_of_register[0].get('id')
                terms_of_concept = TermListQualif.objects.using('decs_portal').filter(identifier_concept_id=id_concept,concept_preferred_term='Y',record_preferred_term='Y')
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

        bundle.data['IdentifierQualif'] = array_fields_all

        # =========================================================================================================================================================================

        # DescriptionQualif
        array_fields = {}
        array_fields_all = []
        results = DescriptionQualif.objects.using('decs_portal').filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["language_code"] = field.language_code
            array_fields["annotation"] = field.annotation
            array_fields["history_note"] = field.history_note
            array_fields["online_note"] = field.online_note

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['DescriptionQualif'] = array_fields_all

        # =========================================================================================================================================================================

        # TreeNumbersListQualif
        array_fields = {}
        array_fields_all = []
        results = TreeNumbersListQualif.objects.using('decs_portal').filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            array_fields["tree_number"] = field.tree_number

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['TreeNumbersListQualif'] = array_fields_all

        # =========================================================================================================================================================================

        # IdentifierConceptListQualif
        array_fields = {}
        array_fields_all = []
        results = IdentifierConceptListQualif.objects.using('decs_portal').filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["id"] = field.id
            identifier_concept_id = field.id
            array_fields["concept_ui"] = field.concept_ui
            array_fields["concept_relation_name"] = field.concept_relation_name
            array_fields["preferred_concept"] = field.preferred_concept
            array_fields["historical_annotation"] = field.historical_annotation

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer descrição dos conceitos
            array_fields_ConceptListQualif = {}
            array_fields_ConceptListQualif_all = []
            ConceptListQualif_results = ConceptListQualif.objects.using('decs_portal').filter(identifier_concept_id=identifier_concept_id)
            for field in ConceptListQualif_results:

                if field.language_code and field.scope_note:
                    # Armazena campos
                    array_fields_ConceptListQualif["id"] = field.id
                    array_fields_ConceptListQualif["language_code"] = field.language_code
                    array_fields_ConceptListQualif["scope_note"] = field.scope_note

                    array_fields_ConceptListQualif_all.append(array_fields_ConceptListQualif)
                    array_fields_ConceptListQualif = {}

            array_fields["ConceptListQualif"] = array_fields_ConceptListQualif_all

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer os termos do conceito
            array_fields_TermListQualif = {}
            array_fields_TermListQualif_all = []
            TermListQualif_results = TermListQualif.objects.using('decs_portal').filter(identifier_concept_id=identifier_concept_id)
            for field in TermListQualif_results:
                # Armazena campos
                if field.status == 1:
                    array_fields_TermListQualif["id"] = field.id
                    identifier_term_id = field.id
                    array_fields_TermListQualif["status"] = field.status
                    array_fields_TermListQualif["term_ui"] = field.term_ui
                    array_fields_TermListQualif["language_code"] = field.language_code
                    array_fields_TermListQualif["term_string"] = field.term_string
                    array_fields_TermListQualif["concept_preferred_term"] = field.concept_preferred_term
                    array_fields_TermListQualif["is_permuted_term"] = field.is_permuted_term
                    array_fields_TermListQualif["lexical_tag"] = field.lexical_tag
                    array_fields_TermListQualif["record_preferred_term"] = field.record_preferred_term
                    array_fields_TermListQualif["entry_version"] = field.entry_version
                    array_fields_TermListQualif["date_created"] = field.date_created
                    array_fields_TermListQualif["date_altered"] = field.date_altered
                    array_fields_TermListQualif["historical_annotation"] = field.historical_annotation
                    array_fields_TermListQualif["term_thesaurus"] = field.term_thesaurus

                    array_fields_TermListQualif_all.append(array_fields_TermListQualif)
                    array_fields_TermListQualif = {}

            array_fields["TermListQualif"] = array_fields_TermListQualif_all


            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['IdentifierConceptListQualif'] = array_fields_all

        return bundle
