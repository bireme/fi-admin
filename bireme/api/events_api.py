# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie import fields

from  events.models import Event

import requests
import urllib

class EventResource(ModelResource):

    class Meta:
        queryset = Event.objects.filter(status=1)
        allowed_methods = ['get']
        resource_name = 'event'
        filtering = {
            'thematic_area_id': 'exact',
        }
        include_resource_uri = False
        max_limit = settings.MAX_EXPORT_API_LIMIT

    def build_filters(self, filters=None):
        orm_filters = super(EventResource, self).build_filters(filters)

        if 'thematic_area_id' in filters:
            orm_filters['thematics__thematic_area__exact'] = filters['thematic_area_id']
        return orm_filters

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/next%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_next'), name="api_get_next"),
            url(r"^(?P<resource_name>%s)/get_last_id%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_last_id'), name="api_get_last_id"),
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
        sort = request.GET.get('sort', 'start_date desc')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:events.event) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:events.event)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main','op': op,'output': 'site', 'lang': lang,
                    'q': q , 'fq': fq,  'start': start, 'count': count, 'id' : id, 'sort': sort}


        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def get_next(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        fq = request.GET.get('fq', '')
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'start_date asc')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:events.event) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:events.event)'

        q = 'start_date:[NOW TO *]'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main','op': op,'output': 'site', 'lang': 'pt',
                    'q': q , 'fq': fq, 'sort': sort}


        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def get_last_id(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        response = Event.objects.latest('pk').pk

        return self.create_response(request, response)
