# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie import fields

from oer.models import *
from attachments.models import Attachment

from  main.models import Descriptor, ResourceThematic
import requests
import urllib

class OERResource(ModelResource):
    resource_type = fields.CharField(attribute='type')
    language = fields.CharField(attribute='language')
    structure = fields.CharField(attribute='structure', null=True)
    interactivity_type = fields.CharField(attribute='interactivity_type', null=True)
    learning_resource_type = fields.CharField(attribute='learning_resource_type', null=True, blank=True)
    interactivity_level = fields.CharField(attribute='interactivity_level', null=True)
    learning_context = fields.CharField(attribute='learning_context', null=True)
    difficulty = fields.CharField(attribute='difficulty', null=True)
    license = fields.CharField(attribute='license', null=True)

    class Meta:
        queryset = OER.objects.filter(status=1)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'oer'
        filtering = {
            'cvsp_node': 'exact',
        }
        include_resource_uri = False

    def build_filters(self, filters=None):
        orm_filters = super(OERResource, self).build_filters(filters)

        if 'cvsp_node' in filters:
            orm_filters['cvsp_node__exact'] = filters['cvsp_node']
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
            fq = '(django_ct:oer.oer) AND %s' % fq
        else:
            fq = '(django_ct:oer.oer)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main','op': op,'output': 'site', 'lang': lang,
                    'q': q , 'fq': fq,  'start': start, 'count': count, 'id' : id,'sort': sort}

        print search_params

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())


    def dehydrate(self, bundle):
        c_type = ContentType.objects.get_for_model(bundle.obj)

        descriptors = Descriptor.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        thematic_areas = ResourceThematic.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)
        attachments = Attachment.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        #urls = OERURL.objects.filter(oer_id=bundle.obj.id)

        # add fields to output
        if bundle.obj.contributor:
            bundle.data['contributor'] = [contributor['text'] for contributor in bundle.obj.contributor]
        if bundle.obj.creator:
            bundle.data['creator'] = [creator['text'] for creator in bundle.obj.creator]
        if bundle.obj.course_type:
            bundle.data['course_type'] = [ct for ct in bundle.obj.course_type.all()]
        if bundle.obj.tec_resource_type:
            bundle.data['tec_resource_type'] = [tec for tec in bundle.obj.tec_resource_type.all()]
        if bundle.obj.format:
            bundle.data['format'] = [tec for tec in bundle.obj.format.all()]
        if bundle.obj.audience:
            bundle.data['audience'] = [audience for audience in bundle.obj.audience.all()]

        # create a single list of urls and attachments associated with the object
        '''
        url_list = [u.url for u in urls]
        for attach in attachments:
            view_url = "%sdocument/view/%s" % (settings.SITE_URL, attach.short_url)
            url_list.append(view_url)

        if url_list:
            bundle.data['url'] = url_list
        '''

        bundle.data['descriptors'] = [{'text': descriptor.text, 'code': descriptor.code} for descriptor in descriptors]
        bundle.data['thematic_areas'] = [{'code': thematic.thematic_area.acronym, 'text': thematic.thematic_area.name} for thematic in thematic_areas]


        return bundle
