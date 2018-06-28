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
        queryset = Collection.objects.filter(parent__isnull=True)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'community'
        include_resource_uri = False


class CollectionResource(ModelResource):
    parent = fields.CharField(attribute='parent', null=True)
    class Meta:
        queryset = Collection.objects.filter(parent__isnull=False)
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'collection'
        filtering = {
            'community': 'exact',
        }
        include_resource_uri = False

    def build_filters(self, filters=None):
        orm_filters = super(CollectionResource, self).build_filters(filters)

        if 'community' in filters:
            orm_filters['parent__exact'] = filters['community']

        return orm_filters

    def dehydrate(self, bundle):
        lang_param = bundle.request.GET.get('lang', 'en')

        if bundle.obj.language != lang_param:
            try:
                translation = CollectionLocal.objects.get(collection=bundle.obj.id, language=lang_param)
                bundle.data['name'] = translation.name
                bundle.data['language'] = translation.language
                bundle.data['description'] = translation.description
                bundle.data['image'] = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, translation.image)
            except CollectionLocal.DoesNotExist:
                # adjust image url in original bundle
                bundle.data['image'] = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, bundle.obj.image)
                pass

        return bundle


class ClassificationResource(ModelResource):
    collection = fields.CharField(attribute='collection', null=True)
    class Meta:
        queryset = Relationship.objects.all().order_by('object_id')
        allowed_methods = ['get']
        serializer = Serializer(formats=['json', 'xml'])
        resource_name = 'classification'
        include_resource_uri = False
