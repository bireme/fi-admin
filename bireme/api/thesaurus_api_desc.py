# coding: utf-8

'''
DESCRIPTORS
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

from thesaurus.field_definitions_desc import field_tag_map

import requests
import urllib
import json

from django.db.models import Q


class ThesaurusResourceDesc(CustomResource):
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
        }
        include_resource_uri = True



    def build_filters(self, filters=None):
        orm_filters = super(ThesaurusResourceDesc, self).build_filters(filters)

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

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:title.title*) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:title.title*)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())



    def dehydrate(self, bundle):

        # 776
        thesaurus_id = IdentifierDesc.objects.filter(id=bundle.obj.id)
        for field in thesaurus_id:
            bundle.data['identifier'] = str(bundle.obj.id).zfill(6)
            # usado para filtrar pesquisa de qualificador
            thesaurus_id_choiced = field.thesaurus_id

        id_concept = IdentifierConceptListDesc.objects.filter(identifier_id=bundle.obj.id,preferred_concept='Y')

        # 'term_string_en': '001',
        term_string_en = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='en',concept_preferred_term='Y',record_preferred_term='Y',status='1')
        for field in term_string_en:
            bundle.data['term_string_en'] = field.term_string

        # 'term_string_es': '002',
        term_string_es = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es',concept_preferred_term='Y',record_preferred_term='Y',status='1')
        for field in term_string_es:
            bundle.data['term_string_es'] = field.term_string

        # 'term_string_pt_br': '003',
        term_string_pt_br = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='pt-br',concept_preferred_term='Y',record_preferred_term='Y',status='1')
        for field in term_string_pt_br:
            bundle.data['term_string_pt_br'] = field.term_string

        # 'term_string_es_es': '004',
        term_string_es_es = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es-es',concept_preferred_term='Y',record_preferred_term='Y',status='1')
        for field in term_string_es_es:
            bundle.data['term_string_es_es'] = field.term_string

        # 'term_string_fr': '016',
        term_string_fr = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='fr',concept_preferred_term='Y',record_preferred_term='Y',status='1')
        for field in term_string_fr:
            bundle.data['term_string_fr'] = field.term_string



        # 'scope_note_en': '005',
        scope_note_en = ConceptListDesc.objects.filter(identifier_concept_id=id_concept,language_code='en')
        for field in scope_note_en:
            bundle.data['scope_note_en'] = '^n' + field.scope_note

        # # 'scope_note_es': '006',
        scope_note_es = ConceptListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es')
        for field in scope_note_es:
            bundle.data['scope_note_es'] = '^n' + field.scope_note

        # # 'scope_note_pt_br': '007',
        scope_note_pt_br = ConceptListDesc.objects.filter(identifier_concept_id=id_concept,language_code='pt-br')
        for field in scope_note_pt_br:
            bundle.data['scope_note_pt_br'] = '^n' + field.scope_note

        # # 'scope_note_es_es': '008',
        scope_note_es_es = ConceptListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es-es')
        for field in scope_note_es_es:
            bundle.data['scope_note_es_es'] = '^n' + field.scope_note



        # 'tree_number': '020',
        tree_number_list = []
        tree_number_arr = TreeNumbersListDesc.objects.filter(identifier_id=bundle.obj.id)
        for field in tree_number_arr:
            item = field.tree_number
            tree_number_list.append(item)
        bundle.data['tree_number'] = tree_number_list



        # Coleta UPs do conceito preferido

        # 'term_string_print_entries_en': '050', # ^i
        term_string_print_entries_en_list = []
        term_string_print_entries_en = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='en',concept_preferred_term='N',record_preferred_term='N',status='1')
        for field in term_string_print_entries_en:
            term_ui_first_letter = field.term_ui[0:1]
            # atribui subcampo t quando o código do termo não for do MESH
            if term_ui_first_letter != 'T':
                item = '^i' + field.term_string + '^tDeCS'
            else:
                item = '^i' + field.term_string
            term_string_print_entries_en_list.append(item)
        bundle.data['term_string_print_entries_en'] = term_string_print_entries_en_list

        # 'term_string_print_entries_es': '050', # ^e
        term_string_print_entries_es_list = []
        term_string_print_entries_es = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es',concept_preferred_term='N',record_preferred_term='N',status='1')
        for field in term_string_print_entries_es:
            item = '^e' + field.term_string
            term_string_print_entries_es_list.append(item)
        bundle.data['term_string_print_entries_es'] = term_string_print_entries_es_list

        # 'term_string_print_entries_pt_br': '050', # ^p
        term_string_print_entries_pt_br_list = []
        term_string_print_entries_pt_br = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='pt-br',concept_preferred_term='N',record_preferred_term='N',status='1')
        for field in term_string_print_entries_pt_br:
            item = '^p' + field.term_string
            term_string_print_entries_pt_br_list.append(item)
        bundle.data['term_string_print_entries_pt_br'] = term_string_print_entries_pt_br_list

        # 'term_string_print_entries_es_es': '050', # ^s
        term_string_print_entries_es_es_list = []
        term_string_print_entries_es_es = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='es-es',concept_preferred_term='N',record_preferred_term='N',status='1')
        for field in term_string_print_entries_es_es:
            item = '^s' + field.term_string
            term_string_print_entries_es_es_list.append(item)
        bundle.data['term_string_print_entries_es_es'] = term_string_print_entries_es_es_list

        # 'term_string_print_entries_fr': '050', # ^f
        term_string_print_entries_fr_list = []
        term_string_print_entries_fr = TermListDesc.objects.filter(identifier_concept_id=id_concept,language_code='fr',concept_preferred_term='N',record_preferred_term='N',status='1')
        for field in term_string_print_entries_fr:
            item = '^f' + field.term_string
            term_string_print_entries_fr_list.append(item)
        bundle.data['term_string_print_entries_fr'] = term_string_print_entries_fr_list



        # Coleta UPs dos conceitos NÃO preferidos
        term_string_print_entries_en_list_NP = []
        term_string_print_entries_es_list_NP = []
        term_string_print_entries_pt_br_list_NP = []
        term_string_print_entries_es_es_list_NP = []
        term_string_print_entries_fr_list_NP = []
        id_concept_nopreferred = IdentifierConceptListDesc.objects.filter(identifier_id=bundle.obj.id,preferred_concept='N')
        for ids_nopreferred in id_concept_nopreferred:

            # 'term_string_print_entries_en': '050', # ^i
            term_string_print_entries_en = TermListDesc.objects.filter(identifier_concept_id=ids_nopreferred,language_code='en',status='1')
            for field in term_string_print_entries_en:
                item = '^i' + field.term_string
                term_string_print_entries_en_list_NP.append(item)
                # print term_string_print_entries_en_list_NP
            bundle.data['term_string_print_entries_en_NP'] = term_string_print_entries_en_list_NP

            # 'term_string_print_entries_es': '050', # ^e
            term_string_print_entries_es = TermListDesc.objects.filter(identifier_concept_id=ids_nopreferred,language_code='es',status='1')
            for field in term_string_print_entries_es:
                item = '^e' + field.term_string
                term_string_print_entries_es_list_NP.append(item)
            bundle.data['term_string_print_entries_es_NP'] = term_string_print_entries_es_list_NP

            # 'term_string_print_entries_pt_br': '050', # ^p
            term_string_print_entries_pt_br = TermListDesc.objects.filter(identifier_concept_id=ids_nopreferred,language_code='pt-br',status='1')
            for field in term_string_print_entries_pt_br:
                item = '^p' + field.term_string
                term_string_print_entries_pt_br_list_NP.append(item)
            bundle.data['term_string_print_entries_pt_br_NP'] = term_string_print_entries_pt_br_list_NP

            # 'term_string_print_entries_es_es': '050', # ^s
            term_string_print_entries_es_es = TermListDesc.objects.filter(identifier_concept_id=ids_nopreferred,language_code='es-es',status='1')
            for field in term_string_print_entries_es_es:
                item = '^s' + field.term_string
                term_string_print_entries_es_es_list_NP.append(item)
            bundle.data['term_string_print_entries_es_es_NP'] = term_string_print_entries_es_es_list_NP

            # 'term_string_print_entries_fr': '050', # ^f
            term_string_print_entries_fr = TermListDesc.objects.filter(identifier_concept_id=ids_nopreferred,language_code='fr',status='1')
            for field in term_string_print_entries_fr:
                item = '^f' + field.term_string
                term_string_print_entries_fr_list_NP.append(item)
            bundle.data['term_string_print_entries_fr_NP'] = term_string_print_entries_fr_list_NP



        # 'term_string_see_related_en': '060', # ^i
        term_string_see_related_en_list=[]
        term_string_see_related_en = SeeRelatedListDesc.objects.filter(identifier_id=bundle.obj.id)
        for field in term_string_see_related_en:
            chk_id = field.descriptor_ui
            if len(chk_id)>0:
                # Quando for um termo que nao eh mesh colocar ^tDeCS
                if field.descriptor_ui[0:1].upper() != 'D':
                    item = '^i' + field.term_string + '^tDeCS'
                else:
                    item = '^i' + field.term_string
            else:
                # Se não existir descriptor_ui colocar ^tr
                item = '^i' + field.term_string + '^tDeCS'
            term_string_see_related_en_list.append(item)
        bundle.data['term_string_see_related_en'] = term_string_see_related_en_list


        # 'decs_code': '099',
        decs_code = IdentifierDesc.objects.filter(id=bundle.obj.id)
        for field in decs_code:
            bundle.data['decs_code'] = str(field.decs_code).zfill(6)



        # 'record_type': '105',
        record_type = IdentifierDesc.objects.filter(id=bundle.obj.id)
        for field in record_type:
            if field.descriptor_class == '1':
                bundle.data['record_type'] = 'H'
            if field.descriptor_class == '2':
                bundle.data['record_type'] = 'T'



        ### 106
        descriptor_type = legacyInformationDesc.objects.filter(identifier_id=bundle.obj.id)
        for field in descriptor_type:
            # c
            # pre_codificado
            # 'descriptor_type_pre_codificado': '106',
            if field.pre_codificado:
                bundle.data['descriptor_type_pre_codificado'] = field.pre_codificado

            # d
            # desastre
            # 'descriptor_type_desastre': '106',
            if field.desastre:
                bundle.data['descriptor_type_desastre'] = field.desastre

            # f
            # reforma_saude
            # 'descriptor_type_reforma_saude': '106',
            if field.reforma_saude:
                bundle.data['descriptor_type_reforma_saude'] = field.reforma_saude

            # g
            # geografico
            # 'descriptor_type_geografico': '106',
            if field.geografico:
                bundle.data['descriptor_type_geografico'] = field.geografico

            # h
            # mesh
            # 'descriptor_type_mesh': '106',
            if field.mesh:
                bundle.data['descriptor_type_mesh'] = field.mesh

            # l
            # pt_lilacs
            # 'descriptor_type_pt_lilacs': '106',
            if field.pt_lilacs:
                bundle.data['descriptor_type_pt_lilacs'] = field.pt_lilacs

            # n
            # nao_indexavel
            # 'descriptor_type_nao_indexavel': '106',
            if field.nao_indexavel:
                bundle.data['descriptor_type_nao_indexavel'] = field.nao_indexavel

            # p
            # homeopatia
            # 'descriptor_type_homeopatia': '106',
            if field.homeopatia:
                bundle.data['descriptor_type_homeopatia'] = field.homeopatia

            # r
            # repidisca
            # 'descriptor_type_repidisca': '106',
            if field.repidisca:
                bundle.data['descriptor_type_repidisca'] = field.repidisca

            # s
            # saude_publica
            # 'descriptor_type_saude_publica': '106',
            if field.saude_publica:
                bundle.data['descriptor_type_saude_publica'] = field.saude_publica

            # x
            # exploded
            # 'descriptor_type_exploded': '106',
            if field.exploded:
                bundle.data['descriptor_type_exploded'] = field.exploded

            # z
            # geog_decs
            # 'descriptor_type_geog_decs': '106',
            if field.geog_decs:
                bundle.data['descriptor_type_geog_decs'] = field.geog_decs



        # 'annotation_en': '110',
        annotation_en = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='en')
        for field in annotation_en:
            if field.annotation:
                bundle.data['annotation_en'] = '^n' + field.annotation

        # 'online_note_en': '117',
        online_note_en = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='en')
        for field in online_note_en:
            if field.online_note:
                bundle.data['online_note_en'] = '^n' + field.online_note

        # 'history_note_en': '119',
        history_note_en = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='en')
        for field in history_note_en:
            if field.history_note:
                bundle.data['history_note_en'] = '^n' + field.history_note



        # 'entrycombination': '170',
        # EntryCombinationListDesc
        entrycombination_en_list = []
        entrycombination_en = EntryCombinationListDesc.objects.filter(identifier_id=bundle.obj.id)
        for field in entrycombination_en:
            ecin_qualif = field.ecin_qualif
            ecin_id = field.ecin_id
            ecout_desc = field.ecout_desc
            ecout_qualif = field.ecout_qualif
            # print '----->', ecin_qualif,'  - ',ecin_id
            # Faz primeiro pesquisa para ver se tem ecin_id (código do qualificador)
            if len(ecin_id)>0:
                # abbrev_en = IdentifierQualif.objects.filter(qualifier_ui=ecin_id,thesaurus_id=ths)
                abbrev_en = IdentifierQualif.objects.filter(qualifier_ui=ecin_id)
                for field in abbrev_en:
                    abbreviation = field.abbreviation
                    # print ' ---> abbrev', abbreviation,' -- ',thesaurus_id_choiced
            else:
                if len(ecin_qualif)>0:
                    # Pesquisa a existencia de term_string para econtrar abreviação
                    terms = TermListQualif.objects.filter( term_thesaurus=thesaurus_id_choiced, term_string=ecin_qualif, language_code='en', concept_preferred_term='Y', record_preferred_term='Y' )
                    for field in terms:
                        identifier_concept_id = field.identifier_concept_id
                        # print ' ---> identifier_concept_id', identifier_concept_id
                        concepts = IdentifierConceptListQualif.objects.filter ( id=identifier_concept_id, preferred_concept='Y' )
                        for field in concepts:
                            identifier_id = field.identifier_id
                            # print ' ---> identifier_id', identifier_id
                            abbrev_en = IdentifierQualif.objects.filter(id=identifier_id)
                            for field in abbrev_en:
                                abbreviation = field.abbreviation
                                # print ' ---> abbrev', abbreviation,' -- ',thesaurus_id_choiced
            # print 'Abreviation---> ',abbreviation,'^i',ecout_desc
            item = abbreviation + '^i' + ecout_desc
            if len(ecout_qualif)>0:
                item = item + '^q' + ecout_qualif
            # print 'item---> ',item

            entrycombination_en_list.append(item)
        bundle.data['entrycombination_en'] = entrycombination_en_list


        # 'pharmacologicalaction_en': '192',
        pharmacologicalaction_en_list = []
        pharmacologicalaction_en = PharmacologicalActionList.objects.filter(identifier_id=bundle.obj.id,language_code='en')
        for field in pharmacologicalaction_en:
            item = field.term_string
            pharmacologicalaction_en_list.append(item)
        bundle.data['pharmacologicalaction_en'] = pharmacologicalaction_en_list


        # 'annotation_es': '210',
        annotation_es = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='es')
        for field in annotation_es:
            if field.annotation:
                bundle.data['annotation_es'] = '^n' + field.annotation

        # 'online_note_es': '217',
        online_note_es = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='es')
        for field in online_note_es:
            if field.online_note:
                bundle.data['online_note_es'] = '^n' + field.online_note

        # 'history_note_es': '219',
        history_note_es = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='es')
        for field in history_note_es:
            if field.history_note:
                bundle.data['history_note_es'] = '^n' + field.history_note



        # 'annotation_pt_br': '310',
        annotation_pt_br = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='pt-br')
        for field in annotation_pt_br:
            if field.annotation:
                bundle.data['annotation_pt_br'] = '^n' + field.annotation

        # 'online_note_pr_br': '317',
        online_note_pt_br = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='pt-br')
        for field in online_note_pt_br:
            if field.online_note:
                bundle.data['online_note_pt_br'] = '^n' + field.online_note

        # 'history_note_pt_br': '319',
        history_note_pt_br = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='pt-br')
        for field in history_note_pt_br:
            if field.history_note:
                bundle.data['history_note_pt_br'] = '^n' + field.history_note

        # 'mesh_id_descriptor_ui': '480',
        mesh_id_descriptor_arr = IdentifierDesc.objects.filter(id=bundle.obj.id)
        for field in mesh_id_descriptor_arr:
            letter_chk = field.descriptor_ui[0:1].upper()
            if letter_chk == 'D':
                bundle.data['mesh_id_descriptor_ui'] = field.descriptor_ui



        # 'consider_also_en': '569',
        consider_also_en = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='en')
        for field in consider_also_en:
            if field.consider_also:
                bundle.data['consider_also_en'] = '^i' + field.consider_also.replace('consider also terms at ','')

        # 'consider_also_es': '569',
        consider_also_es = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='es')
        for field in consider_also_es:
            if field.consider_also:
                bundle.data['consider_also_es'] = '^e' + field.consider_also

        # 'consider_also_pt_br': '569',
        consider_also_pt_br = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='pt-br')
        for field in consider_also_pt_br:
            if field.consider_also:
                bundle.data['consider_also_pt_br'] = '^p' + field.consider_also

        # 'consider_also_es_es': '569',
        consider_also_es_es = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='es-es')
        for field in consider_also_es_es:
            if field.consider_also:
                bundle.data['consider_also_es_es'] = '^s' + field.consider_also

        # 'consider_also_fr': '569',
        consider_also_fr = DescriptionDesc.objects.filter(identifier_id=bundle.obj.id,language_code='fr')
        for field in consider_also_fr:
            if field.consider_also:
                bundle.data['consider_also_fr'] = '^f' + field.consider_also


        # 'allowed_qualifiers': '950',
        id_abbrev = IdentifierDesc.objects.filter(id=bundle.obj.id).values('abbreviation')
        allowed_qualifiers = IdentifierQualif.objects.filter(id__in=id_abbrev).order_by('abbreviation')
        allowed_qualifiers_concat = ''
        for field in allowed_qualifiers:
            item = field.abbreviation
            allowed_qualifiers_concat = allowed_qualifiers_concat + ' ' + item
        bundle.data['allowed_qualifiers'] = allowed_qualifiers_concat

        # Fazer filtro pelos conceitos do registro
        # Entrar em cada familia do conceito e analisar seus termos
        # 'historical_annotation': '998',
        lista_maior=[]
        x_array=[]
        concept_arr = IdentifierConceptListDesc.objects.filter(identifier_id=bundle.obj.id).values('id')
        for concept_id in concept_arr:
            c_id=concept_id.get('id')
            bundle.data['historical_annotation'] = c_id

            q_published = Q(identifier_concept_id=c_id,status='1')
            q_historical = Q(identifier_concept_id=c_id,status='5')
            historical_annotation_concat = ''

            # ingles
            q_language = Q(language_code='en')
            historical_annotation_en = TermListDesc.objects.filter( ( q_published | q_historical ) & q_language ).values('historical_annotation')
            for field in historical_annotation_en:
                t=field.get('historical_annotation')
                if len(t)>0:
                    t=t.replace('^i','^h')
                    x_array.append(t)
            if len(x_array)>0:
                historical_annotation_concat_en=x_array
                lista_maior=historical_annotation_concat_en

            # espanhol
            q_language = Q(language_code='es')
            historical_annotation_es = TermListDesc.objects.filter( ( q_published | q_historical ) & q_language ).values('historical_annotation')
            for field in historical_annotation_es:
                t=field.get('historical_annotation')
                if len(t)>0:
                    t=t.replace('^e','^h')
                    x_array.append(t)
            if len(x_array)>0:
                historical_annotation_concat_es=x_array
                lista_maior=historical_annotation_concat_es

            # português
            q_language = Q(language_code='pt-br')
            historical_annotation_pt_br = TermListDesc.objects.filter( ( q_published | q_historical ) & q_language ).values('historical_annotation')
            for field in historical_annotation_pt_br:
                t=field.get('historical_annotation')
                if len(t)>0:
                    t=t.replace('^p','^h')
                    x_array.append(t)
            if len(x_array)>0:
                historical_annotation_concat_pt_br=x_array
                lista_maior=historical_annotation_concat_pt_br

        bundle.data['historical_annotation'] = lista_maior

        return bundle
