# coding: utf-8
from django.conf import settings
from django.urls import re_path
from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from tastypie import fields

from main.models import Descriptor, ResourceThematic
from attachments.models import Attachment
from leisref.models import Act, ActURL

import requests
import urllib
import json

class LeisrefResource(ModelResource):

    class Meta:
        queryset = Act.objects.filter(status=1)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'leisref'
        filtering = {
            'update_date': ('gte', 'lte'),
            'status': 'exact',
            'collection': ALL,
        }
        include_resource_uri = False
        max_limit = settings.MAX_EXPORT_API_LIMIT

    def build_filters(self, filters=None, *args, **kwargs):
        orm_filters = super(LeisrefResource, self).build_filters(filters, *args, **kwargs)

        if 'collection' in filters:
            filter_col_id = filters['collection']
            orm_filters['collection__collection_id'] = filter_col_id

        return orm_filters


    def prepend_urls(self):
        return [
            re_path(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        q = request.GET.get('q', '')
        fq = request.GET.get('fq', '')
        fb = request.GET.get('fb', '')
        start = request.GET.get('start', 0)
        count = request.GET.get('count', 0)
        lang = request.GET.get('lang', 'pt')
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'publication_date desc')
        facet_list = request.GET.getlist('facet.field', [])

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:leisref.act) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:leisref.act)'

        if id != '':
            q = 'id:%s' % id

        # url
        search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op,'output': 'site', 'lang': lang,
                         'q': q, 'fq': [fq], 'fb': fb, 'start': int(start), 'count': int(count), 'sort': sort}

        if facet_list:
            search_params['facet.field'] = []
            for facet_field in facet_list:
                search_params['facet.field'].append(facet_field)
                facet_limit_param = 'f.{}.facet.limit'.format(facet_field)
                facet_field_limit = request.GET.get(facet_limit_param, None)
                if facet_field_limit:
                    search_params[facet_limit_param] = facet_field_limit


        search_params_json = json.dumps(search_params)
        request_headers = {'apikey': settings.SEARCH_SERVICE_APIKEY}

        r = requests.post(search_url, data=search_params_json, headers=request_headers)
        try:
            response_json = r.json()
        except ValueError:
            response_json = json.loads('{"type": "error", "message": "invalid output"}')

        # Duplicate "response" to "match" element for old compatibility calls
        if id != '' and response_json:
            response_json['diaServerResponse'][0]['match'] = response_json['diaServerResponse'][0]['response']

        self.log_throttled_access(request)
        return self.create_response(request, response_json)

    def dehydrate(self, bundle):
        c_type = ContentType.objects.get_for_model(bundle.obj)

        descriptors = Descriptor.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        thematic_areas = ResourceThematic.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)
        attachments = Attachment.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        urls = ActURL.objects.filter(act_id=bundle.obj.id)

        # add fields to output
        bundle.data['descriptors'] = [{'text': descriptor.text, 'code': descriptor.code} for descriptor in descriptors]
        bundle.data['thematic_areas'] = [{'code': thematic.thematic_area.acronym, 'text': thematic.thematic_area.name} for thematic in thematic_areas]

        # add fields to output
        if bundle.obj.act_type:
            bundle.data['act_type'] = "|".join(bundle.obj.act_type.get_translations())
        if bundle.obj.organ_issuer:
            bundle.data['organ_issuer'] = "|".join(bundle.obj.organ_issuer.get_translations())
        if bundle.obj.source_name:
            bundle.data['source_name'] = "|".join(bundle.obj.source_name.get_translations())
        if bundle.obj.scope_region:
            bundle.data['scope_region'] = "|".join(bundle.obj.scope_region.get_translations())


        # check if object has classification (relationship model)
        if bundle.obj.collection.exists():
            community_list = []
            collection_list = []

            collection_all = bundle.obj.collection.all()
            for rel in collection_all:
                collection_labels = "|".join(rel.collection.get_translations())
                collection_item = u"{}|{}".format(rel.collection.id, collection_labels)
                collection_list.append(collection_item)
                if rel.collection.parent:
                    community_labels = "|".join(rel.collection.parent.get_translations())
                    community_item = u"{}|{}".format(rel.collection.parent.id, community_labels)
                    community_list.append(community_item)

            bundle.data['community'] = community_list
            bundle.data['collection'] = collection_list

        # add eletronic_address
        electronic_address = []
        for attach in attachments:
            file_name = attach.attachment_file.name
            file_extension = file_name.split(".")[-1].lower()

            if file_extension == 'pdf':
                file_type = 'PDF'
            else:
                file_type = 'TEXTO'

            view_url = "%sdocument/view/%s" % (settings.SITE_URL,  attach.short_url)

            electronic_address.append({'_u': view_url, '_i': attach.language[:2],
                                       '_y': file_type, '_q': file_extension})
        for url in urls:
            electronic_address.append({'_u': url.url, '_i': url.language[:2]})

        if electronic_address:
            bundle.data['electronic_address'] = electronic_address


        return bundle
