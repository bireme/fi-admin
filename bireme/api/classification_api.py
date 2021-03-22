# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, url, include

from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie import fields

from classification.models import *

import requests
import urllib

class CommunityResource(ModelResource):
    class Meta:
        queryset = Collection.objects.filter(community_flag=True)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'community'
        filtering = {
            'community': 'exact',
            'country': 'exact',
        }
        include_resource_uri = False
        max_limit = settings.MAX_EXPORT_API_LIMIT

    def build_filters(self, filters=None):
        orm_filters = super(CommunityResource, self).build_filters(filters)

        if 'community' in filters:
            orm_filters['id__exact'] = filters['community']

        if 'country' in filters:
            orm_filters['country__exact'] = filters['country']

        return orm_filters

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/get_country_list%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_country_list'), name="api_get_country_list"),
        ]

    def dehydrate(self, bundle):
        lang_param = bundle.request.GET.get('lang', 'en')
        # lang param compatibility with 2 letters calls
        if lang_param and lang_param == 'pt':
            lang_param = 'pt-br'

        community_image = bundle.obj.image
        if bundle.obj.language != lang_param:
            try:
                translation = CollectionLocal.objects.filter(collection=bundle.obj.id, language=lang_param).first()
                if translation:
                    bundle.data['name'] = translation.name
                    bundle.data['language'] = translation.language
                    bundle.data['description'] = translation.description
                    if translation.image:
                        community_image = translation.image
            except CollectionLocal.DoesNotExist:
                pass

        # adjust image url
        if community_image:
            bundle.data['image'] = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, community_image)

        return bundle

    def get_country_list(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        community_list = Collection.objects.filter(community_flag=True, country__isnull=False)
        country_list = [community.country for community in community_list]
        country_list_unique = set(country_list)
        country_list_detail = [{'name': c.get_translations(), 'id': c.id, 'code': c.code} for c in country_list_unique]

        return self.create_response(request, country_list_detail)


class CollectionResource(ModelResource):
    parent = fields.CharField(attribute='parent', null=True)
    class Meta:
        queryset = Collection.objects.filter(parent__isnull=False)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'collection'
        filtering = {
            'community': 'exact',
            'collection': 'exact',
        }
        include_resource_uri = False

    def build_filters(self, filters=None):
        orm_filters = super(CollectionResource, self).build_filters(filters)

        if 'community' in filters:
            orm_filters['parent__exact'] = filters['community']

        if 'collection' in filters:
            orm_filters['id__exact'] = filters['collection']

        return orm_filters

    def dehydrate(self, bundle):
        lang_param = bundle.request.GET.get('lang', 'en')
        # lang param compatibility with 2 letters calls
        if lang_param and lang_param == 'pt':
            lang_param = 'pt-br'

        collection_image = bundle.obj.image
        if bundle.obj.language != lang_param:
            try:
                translation = CollectionLocal.objects.filter(collection=bundle.obj.id, language=lang_param).first()
                if translation:
                    bundle.data['name'] = translation.name
                    bundle.data['language'] = translation.language
                    bundle.data['description'] = translation.description
                    if translation.image:
                        collection_image = translation.image
            except CollectionLocal.DoesNotExist:
                pass


        # adjust image url
        if collection_image:
            bundle.data['image'] = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, collection_image)

        # remove country name from collection parent name
        if bundle.obj.parent:
            bundle.data['parent'] = bundle.obj.parent.name

        return bundle


class ClassificationResource(ModelResource):
    collection = fields.CharField(attribute='collection', null=True)
    class Meta:
        queryset = Relationship.objects.all().order_by('object_id')
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'classification'
        include_resource_uri = False
