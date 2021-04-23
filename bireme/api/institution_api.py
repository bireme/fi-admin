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
        max_limit = settings.MAX_EXPORT_API_LIMIT

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

        # filter result by approved resources (status=1)
        if fq != '':
            fq = '(django_ct:institution.institution) AND %s' % fq
        else:
            fq = '(django_ct:institution.institution)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def dehydrate(self, bundle):
        contact_person_list = []
        contact_email_list = []
        contact_phone_list = []
        category_list = []
        type_list = []

        try:
            adm = Adm.objects.get(institution=bundle.obj.id)
        except Adm.DoesNotExist:
            adm = None

        if adm:
            for category in adm.category.all():
                category_list.append(category.name)

            for type in adm.type.all():
                type_list.append(type.name)

        contact_list = Contact.objects.filter(institution=bundle.obj.id)
        if contact_list:
            for contact in contact_list:
                if contact.name:
                    contact_person_list.append("^a%s^b%s^c%s" % (contact.name, contact.prefix, contact.job_title))
                if contact.email:
                    contact_email_list.append(contact.email)
                if contact.phone_number:
                    bundle.data['country_area_code'] = contact.country_area_code
                    contact_phone_list.append(contact.phone_number)

        unitlevel_list = UnitLevel.objects.filter(institution=bundle.obj.id).order_by('level')
        if unitlevel_list:
            for unitlevel in unitlevel_list:
                field_name = "unit_%s" % unitlevel.level
                bundle.data[field_name] = "^a%s^b%s" % (unitlevel.unit.name, unitlevel.unit.acronym)

        url_list = URL.objects.filter(institution=bundle.obj.id)

        # add fields to output
        bundle.data['MFN'] = bundle.obj.id
        if bundle.obj.acronym:
            bundle.data['name'] = "^a%s^b%s" % (bundle.obj.name, bundle.obj.acronym)
        else:
            bundle.data['name'] = "^a%s" % bundle.obj.name

        bundle.data['category'] = category_list
        bundle.data['type'] = type_list
        if bundle.obj.city:
            bundle.data['city'] = "^a%s" % bundle.obj.city
        if bundle.obj.state:
            bundle.data['state'] = "^a%s" % bundle.obj.state
        if bundle.obj.country:
            bundle.data['country'] = "^a%s" % bundle.obj.country.code
        if bundle.obj.zipcode:
            bundle.data['zipcode'] = "^b%s" % bundle.obj.zipcode
        if contact_person_list:
            bundle.data['contact_person'] = contact_person_list
        if contact_email_list:
            bundle.data['contact_email'] = contact_email_list
        if contact_phone_list:
            bundle.data['contact_phone'] = contact_phone_list
        if url_list:
            bundle.data['url'] = [u.url for u in url_list]

        return bundle
