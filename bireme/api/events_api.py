# coding: utf-8
from django.conf import settings
from django.urls import re_path

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie import fields

from  events.models import Event

import requests
import urllib
import json

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

    def build_filters(self, filters=None, *args, **kwargs):
        orm_filters = super(EventResource, self).build_filters(filters, *args, **kwargs)

        if 'thematic_area_id' in filters:
            orm_filters['thematics__thematic_area__exact'] = filters['thematic_area_id']
        return orm_filters

    def prepend_urls(self):
        return [
            re_path(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
            re_path(r"^(?P<resource_name>%s)/next%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_next'), name="api_get_next"),
            re_path(r"^(?P<resource_name>%s)/get_last_id%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_last_id'), name="api_get_last_id"),
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
        sort = request.GET.get('sort', 'start_date desc')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:events.event) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:events.event)'

        if id != '':
            q = 'id:%s' % id

        # url
        search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op,'output': 'site', 'lang': lang,
                    'q': q , 'fq': [fq], 'fb': fb, 'start': int(start), 'count': int(count), 'sort': sort}


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

    def get_next(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        fq = request.GET.get('fq', '')
        fb = request.GET.get('fb', '')
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'start_date asc')
        count = request.GET.get('count', 0)

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:events.event) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:events.event)'

        q = 'start_date:[NOW TO *]'

        # url
        search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op,'output': 'site', 'lang': 'pt',
                    'q': q , 'fq': [fq], 'fb': fb, 'sort': sort, 'count': int(count)}


        search_params_json = json.dumps(search_params)
        request_headers = {'apikey': settings.SEARCH_SERVICE_APIKEY}

        r = requests.post(search_url, data=search_params_json, headers=request_headers)
        try:
            response_json = r.json()
        except ValueError:
            response_json = json.loads('{"type": "error", "message": "invalid output"}')

        self.log_throttled_access(request)
        return self.create_response(request, response_json)

    def get_last_id(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        response = Event.objects.latest('pk').pk

        return self.create_response(request, response)
