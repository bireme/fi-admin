# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie import fields

from multimedia.models import Media

from  main.models import Descriptor, ResourceThematic
import requests
import urllib

class MediaResource(ModelResource):

    class Meta:
        queryset = Media.objects.filter(status=1)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'multimedia'
        filtering = {
            'thematic_area_id': 'exact',
        }
        include_resource_uri = False
        max_limit = settings.MAX_EXPORT_API_LIMIT

    def build_filters(self, filters=None):
        orm_filters = super(MediaResource, self).build_filters(filters)

        if 'thematic_area_id' in filters:
            orm_filters['thematics__thematic_area__exact'] = filters['thematic_area_id']
        return orm_filters

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
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
            fq = '(status:1 AND django_ct:multimedia.media) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:multimedia.media)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main','op': op,'output': 'site', 'lang': lang,
                    'q': q , 'fq': fq,  'start': start, 'count': count, 'id' : id,'sort': sort}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())


    def dehydrate(self, bundle):
        c_type = ContentType.objects.get_for_model(bundle.obj)

        descriptors = Descriptor.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        thematic_areas = ResourceThematic.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)

        # add fields to output
        bundle.data['descriptors'] = [{'text': descriptor.text, 'code': descriptor.code} for descriptor in descriptors]
        bundle.data['thematic_areas'] = [{'code': thematic.thematic_area.acronym, 'text': thematic.thematic_area.name} for thematic in thematic_areas]
        bundle.data['authors'] = [line.strip() for line in bundle.obj.authors.split('\n') if line.strip()]
        bundle.data['contributors'] = [line.strip() for line in bundle.obj.contributors.split('\n') if line.strip()]

        return bundle
