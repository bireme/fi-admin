# coding: utf-8
from django.conf import settings
from django.urls import re_path
from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from tastypie import fields

from multimedia.models import Media

from  main.models import Descriptor, ResourceThematic, Keyword
import requests
import urllib
import json

class MediaResource(ModelResource):

    class Meta:
        queryset = Media.objects.filter(status=1)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'multimedia'
        filtering = {
            'thematic_area_id': 'exact',
            'collection': ALL,
        }
        include_resource_uri = False
        max_limit = settings.MAX_EXPORT_API_LIMIT

    def build_filters(self, filters=None, *args, **kwargs):
        orm_filters = super(MediaResource, self).build_filters(filters, *args, **kwargs)

        if 'thematic_area_id' in filters:
            orm_filters['thematics__thematic_area__exact'] = filters['thematic_area_id']

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
        sort = request.GET.get('sort', 'created_date desc')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:multimedia.media) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:multimedia.media)'

        if id != '':
            q = 'id:%s' % id

        # url
        search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op,'output': 'site', 'lang': lang,
                    'q': q , 'fq': [fq], 'fb': fb, 'start': int(start), 'count': int(count),'sort': sort}

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
        keywords = Keyword.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        thematic_areas = ResourceThematic.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)

        # add fields to output
        bundle.data['descriptors'] = [{'text': descriptor.text, 'code': descriptor.code} for descriptor in descriptors]
        bundle.data['keywords'] = [keyword.text for keyword in keywords]

        bundle.data['thematic_areas'] = [{'code': thematic.thematic_area.acronym, 'text': thematic.thematic_area.name} for thematic in thematic_areas]
        bundle.data['authors'] = [line.strip() for line in bundle.obj.authors.split('\n') if line.strip()]
        bundle.data['contributors'] = [line.strip() for line in bundle.obj.contributors.split('\n') if line.strip()]
        bundle.data['related_links'] = [line.strip() for line in bundle.obj.related_links.split('\n') if line.strip()]

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


        return bundle
