# coding: utf-8
from django.conf import settings
from django.conf.urls.defaults import *

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie import fields

from  events.models import Event

import requests
import urllib

class EventResource(ModelResource):

    class Meta:
        queryset = Event.objects.all()
        allowed_methods = ['get']
        resource_name = 'event'

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
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'created_date desc')        

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:events.event) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:events.event)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fiadmin', 'col': 'main','op': op,'output': 'site', 'lang': 'pt', 
                    'q': q , 'fq': fq,  'start': start, 'count': count, 'id' : id,'sort': sort}

        r = requests.post(search_url, data=search_params)        

        self.log_throttled_access(request)
        return self.create_response(request, r.json())
        
