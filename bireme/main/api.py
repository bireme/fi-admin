# coding: utf-8
from django.conf import settings
from django.conf.urls.defaults import *

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie import fields
import models
import requests
import urllib

class ResourceAPI(ModelResource):
    # descriptors relationship 
    descriptors = fields.ToManyField('main.api.DescriptorResource', 'resources', related_name='resource', full=True, null=True)

    class Meta:
        queryset = models.Resource.objects.all()
        allowed_methods = ['get']
        resource_name = 'resource'

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

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'lis', 'col': 'main','op': 'search', 
                    'output': 'site', 'lang': 'pt', 'q': q , 'fq': fq,  'start': start, 'count': count}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())
        
class DescriptorResource(ModelResource):    
    resource = fields.ToOneField('main.api.ResourceAPI', 'resource')

    class Meta:
        queryset = models.Descriptor.objects.all()
        resource_name = 'descriptor'
