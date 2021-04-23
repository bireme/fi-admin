# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib.contenttypes.models import ContentType

from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from title.models import *
from isis_serializer import ISISSerializer

from tastypie_custom import CustomResource

from main.models import Descriptor
from title.field_definitions import field_tag_map, issue_field_tag_map

import requests
import urllib
import json

TITLE_VARIANCE_LABELS = (
    ('230', 'parallel_titles'),
    ('235', 'shortened_parallel_titles'),
    ('240', 'other_titles'),
)

AUDIT_LABELS = (
    ('510', 'has_edition'),
    ('520', 'is_edition'),
    ('530', 'has_subseries'),
    ('540', 'is_subseries'),
    ('550', 'has_supplement'),
    ('560', 'is_supplement'),
    ('610', 'continuation'),
    ('620', 'partial_continuation'),
    ('650', 'absorbed'),
    ('660', 'absorbed_in_part'),
    ('670', 'subdivision'),
    ('680', 'fusion'),
    ('710', 'continued_by'),
    ('720', 'continued_in_part_by'),
    ('750', 'absorbed_by'),
    ('760', 'absorbed_in_part_by'),
    ('770', 'subdivided'),
    ('780', 'merged'),
    ('790', 'to_form'),
)

class TitleResource(CustomResource):

    class Meta:
        queryset = Title.objects.all()
        allowed_methods = ['get']
        serializer = ISISSerializer(formats=['json', 'xml', 'isis_id'], field_tag=field_tag_map)
        resource_name = 'title'
        filtering = {
            'update_date': ('gte', 'lte'),
            'status': 'exact',
        }
        include_resource_uri = True

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
            fq = '(status:1 AND django_ct:title.title*) AND %s' % fq
        else:
            fq = '(status:1 AND django_ct:title.title*)'

        # url
        search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': fq, 'start': start, 'count': count, 'id': id, 'sort': sort}

        r = requests.post(search_url, data=search_params)

        self.log_throttled_access(request)
        return self.create_response(request, r.json())

    def dehydrate(self, bundle):
        c_type = ContentType.objects.get_for_model(bundle.obj)

        descriptors = Descriptor.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        title_variance = TitleVariance.objects.filter(title=bundle.obj.id)
        bvs_specialties = BVSSpecialty.objects.filter(title=bundle.obj.id)
        index_range = IndexRange.objects.filter(title=bundle.obj.id)
        audits = Audit.objects.filter(title=bundle.obj.id)
        new_url = OnlineResources.objects.filter(title=bundle.obj.id)
        collections = Collection.objects.filter(title=bundle.obj.id)

        # m2m fields
        country = bundle.obj.country.all()
        text_language = bundle.obj.text_language.all()
        abstract_language = bundle.obj.abstract_language.all()
        users = bundle.obj.users.all()

        # add fields to output
        bundle.data['MFN'] = bundle.obj.id
        bundle.data['country'] = [c.code for c in country] # field tag 310
        bundle.data['text_language'] = [tl.acronym for tl in text_language] # field tag 350
        bundle.data['abstract_language'] = [al.acronym for al in abstract_language] # field tag 360
        bundle.data['descriptors'] = [descriptor.text for descriptor in descriptors] # field tag 440
        bundle.data['users'] = [user.code for user in users] # field tag 445

        # field tags 230 and 240
        if title_variance:
            for label in TITLE_VARIANCE_LABELS:
                bundle.data[label[1]] = []

            for title in title_variance:
                text = title.label if title.label else ''
                text += '^a'+title.initial_year if title.initial_year else ''
                text += '^v'+title.initial_volume if title.initial_volume else ''
                text += '^n'+title.initial_number if title.initial_number else ''
                text += '^i'+title.issn if title.issn else ''
                bundle.data[dict(TITLE_VARIANCE_LABELS)[title.type]] += [text]

        # field tag 436
        if bvs_specialties:
            bundle.data['bvs_specialties'] = []
            for bvs_specialty in bvs_specialties:
                text = '^a'+bvs_specialty.bvs if bvs_specialty.bvs else ''
                text += '^b'+bvs_specialty.thematic_area if bvs_specialty.thematic_area else ''
                bundle.data['bvs_specialties'] += [text]

        # field tag 450
        if index_range:
            bundle.data['index_range'] = []
            for index in index_range:
                text = index.index_code.code if index.index_code else ''
                text += '^a'+index.initial_volume if index.initial_volume else ''
                text += '^b'+index.initial_number if index.initial_number else ''
                text += '^c'+index.initial_date if index.initial_date else ''
                text += '^d'+index.final_volume if index.final_volume else ''
                text += '^e'+index.final_number if index.final_number else ''
                text += '^f'+index.final_date if index.final_date else ''
                text += '^g'+index.indexer_cc_code if index.indexer_cc_code else ''
                text += '^h'+str(int(index.distribute)) if index.distribute else '' # boolean field
                text += '^i'+index.copy if index.copy else ''
                text += '^j'+str(int(index.selective)) if index.selective else '' # boolean field
                bundle.data['index_range'] += [text]

        # field tags 510, 520, 530, 540, 550, 560, 610, 620, 650,
        # 660, 670, 680, 710, 720, 750, 760, 770, 780 and 790
        if audits:
            for label in AUDIT_LABELS:
                bundle.data[label[1]] = []

            for audit in audits:
                text = audit.label if audit.label else ''
                text += '^i'+audit.issn if audit.issn else ''
                bundle.data[dict(AUDIT_LABELS)[audit.type]] += [text]

        # field tags 880 and 999
        if new_url:
            bundle.data['online'] = []
            bundle.data['online_notes'] = []

            for index, data in enumerate(new_url):
                text = data.issn_online if data.issn_online else ''
                text += '^a'+data.access_type if data.access_type else ''
                text += '^b'+data.url if data.url else ''
                text += '^c'+data.owner.owner if data.owner else ''
                text += '^d'+data.access_control if data.access_control else ''
                text += '^e'+data.initial_period if data.initial_period else ''
                text += '^f'+data.final_period if data.final_period else ''

                index = '^z'+str(index+1) if text else ''

                if data.notes:
                    if isinstance(data.notes, basestring) and "\r\n" in data.notes:
                        lines = ''
                        for line in data.notes.split('\r\n'):
                            if line:
                                lines += line + ' ' if line[-1] == '.' else line + '. '
                        if lines:
                            bundle.data['online_notes'] += [lines+index]
                            # text += '^g'+lines
                    else:
                        bundle.data['online_notes'] += [data.notes+index]
                        # text += '^g'+data.notes
                else:
                    bundle.data['online_notes'] += ['^xempty'+index]

                bundle.data['online'] += [text+index] if text else ''

        # field tag 998
        if collections:
            format = bundle.request.GET.get('format', None)
            if format == 'isis_id':
                bundle.data['collection'] = []
                for collection in collections:
                    for line in collection.collection.split('\r\n'):
                        bundle.data['collection'] += [line]
            else:
                bundle.data['collection'] = [collection.collection for collection in collections]

        return bundle

class IssueResource(CustomResource):
    title = fields.CharField(attribute='title__id', null=True)
    mask = fields.CharField(attribute='mask__mask', null=True)
    class Meta:
        queryset = Issue.objects.all()
        allowed_methods = ['get']
        serializer = ISISSerializer(formats=['json', 'xml', 'isis_id'], field_tag=issue_field_tag_map)
        resource_name = 'issues'
        include_resource_uri = False
        filtering = {
            'title': ALL,
            'cc': 'exact',
        }

    def build_filters(self, filters=None):
        orm_filters = super(IssueResource, self).build_filters(filters)

        if 'title' in filters:
            filter_title = filters['title']
            orm_filters['title__exact'] = filter_title

        if 'cc' in filters:
            orm_filters['cooperative_center_code__exact'] = filters['cc']

        return orm_filters

    def dehydrate(self, bundle):
        bundle.data['notes'] = []
        bundle.data['record_type'] = bundle.obj.title.record_type

        if bundle.obj.notes:
            if isinstance(bundle.obj.notes, basestring) and "\r\n" in bundle.obj.notes:
                lines = ''
                for line in bundle.obj.notes.split('\r\n'):
                    if line:
                        lines += line + ' ' if line[-1] == '.' else line + '. '
                if lines:
                    bundle.data['notes'] += [lines]
            else:
                bundle.data['notes'] += [bundle.obj.notes]

        return bundle
