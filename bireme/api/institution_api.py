# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf import settings
from copy import copy

from django.contrib.contenttypes.models import ContentType

from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL
from tastypie import fields
from tastypie_custom import CustomResource

from institution.models import *
from isis_serializer import ISISSerializer

from institution.field_definitions import field_tag_map

import os
import requests
import urllib
import json


class InstitutionResource(CustomResource):
    class Meta:
        queryset = Institution.objects.all()
        allowed_methods = ['get']
        serializer = ISISSerializer(formats=['json', 'xml', 'isis_id'], field_tag=field_tag_map)
        resource_name = 'institution'
        filtering = {
            'updated_time': ('gte', 'lte'),
            'status': 'exact',
            'id': ALL
        }
        include_resource_uri = True

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/get_last_id%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_id'), name="api_get_last_id"),
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
        sort = request.GET.get('sort', 'publication_date desc')

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(status:1 AND django_ct:institution.institution) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:institution.institution)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': 'fi', 'col': 'main', 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def dehydrate(self, bundle):

        # add fields to output
        bundle.data['MFN'] = bundle.obj.id


        return bundle
