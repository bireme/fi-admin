# coding: utf-8

'''
Script utilizado para extrair elementos para criacao de XML
http://fi-admin.beta.bvsalud.org/api/desc/index/thesaurus/?format=json&ths=1&decs_code=55123
http://fi-admin.beta.bvsalud.org/api/qualif/index/thesaurus/?format=json&ths=1&decs_code=22003
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
import operator

from django.db.models import Q



class ThesaurusAPIDescResourceIndex(CustomResource):
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
        orm_filters = super(ThesaurusAPIDescResourceIndex, self).build_filters(filters)

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

        id = IdentifierDesc.objects.filter(id=bundle.obj.id).values('id')
        for field in id:
            identifier_id = bundle.obj.id

        # =========================================================================================================================================================================

        # TreeNumbersListDesc
        array_fields = {}
        array_fields_all = []
        results = TreeNumbersListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            array_fields["tree_number"] = field.tree_number

            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['TreeNumbersListDesc'] = array_fields_all

        # =========================================================================================================================================================================

        # IdentifierConceptListDesc
        array_fields = {}
        array_fields_all = []
        results = IdentifierConceptListDesc.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            identifier_concept_id = field.id
            array_fields["concept_ui"] = field.concept_ui
            array_fields["preferred_concept"] = field.preferred_concept

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer os termos do conceito
            array_fields_TermListDesc = {}
            array_fields_TermListDesc_all = []
            TermListDesc_results = TermListDesc.objects.filter(identifier_concept_id=identifier_concept_id)
            for field in TermListDesc_results:
                # Armazena campos
                if field.status == 1:
                    identifier_term_id = field.id
                    array_fields_TermListDesc["language_code"] = field.language_code
                    array_fields_TermListDesc["term_string"] = field.term_string
                    array_fields_TermListDesc["concept_preferred_term"] = field.concept_preferred_term
                    array_fields_TermListDesc["is_permuted_term"] = field.is_permuted_term
                    array_fields_TermListDesc["record_preferred_term"] = field.record_preferred_term

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



class ThesaurusAPIQualifResourceIndex(CustomResource):
    class Meta:
        queryset = IdentifierQualif.objects.all()
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
        orm_filters = super(ThesaurusAPIQualifResourceIndex, self).build_filters(filters)

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

        id = IdentifierQualif.objects.filter(id=bundle.obj.id).values('id')
        for field in id:
            # bundle.data['id'] = str(bundle.obj.id)
            identifier_id = bundle.obj.id

        # =========================================================================================================================================================================

        # TreeNumbersListQualif
        array_fields = {}
        array_fields_all = []
        results = TreeNumbersListQualif.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
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
        results = IdentifierConceptListQualif.objects.filter(identifier_id=identifier_id)
        for field in results:
            # Armazena campos
            identifier_concept_id = field.id
            array_fields["concept_ui"] = field.concept_ui
            array_fields["preferred_concept"] = field.preferred_concept

            # =========================================================================================================================================================================
            # Faz pesquisa para trazer os termos do conceito
            array_fields_TermListQualif = {}
            array_fields_TermListQualif_all = []
            TermListQualif_results = TermListQualif.objects.filter(identifier_concept_id=identifier_concept_id)
            for field in TermListQualif_results:
                # Armazena campos
                if field.status == 1:
                    identifier_term_id = field.id
                    array_fields_TermListQualif["language_code"] = field.language_code
                    array_fields_TermListQualif["term_string"] = field.term_string
                    array_fields_TermListQualif["concept_preferred_term"] = field.concept_preferred_term
                    array_fields_TermListQualif["is_permuted_term"] = field.is_permuted_term
                    array_fields_TermListQualif["record_preferred_term"] = field.record_preferred_term

                    # Armazena array
                    array_fields_TermListQualif_all.append(array_fields_TermListQualif)
                    array_fields_TermListQualif = {}

            array_fields["TermListQualif"] = array_fields_TermListQualif_all


            # Armazena array
            array_fields_all.append(array_fields)

            # Zera array pra próxima leitura
            array_fields = {}

        bundle.data['IdentifierConceptListQualif'] = array_fields_all

        return bundle
