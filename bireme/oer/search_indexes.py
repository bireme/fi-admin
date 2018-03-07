import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, ResourceThematic
from attachments.models import Attachment
from django.conf import settings
from models import *

import json

from django.contrib.contenttypes.models import ContentType

class OERIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    learning_objectives = indexes.CharField(model_attr='learning_objectives')
    description = indexes.CharField(model_attr='description', null=True)
    author = indexes.MultiValueField()
    contributors = indexes.MultiValueField()
    descriptor = indexes.MultiValueField()
    link = indexes.MultiValueField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return OER

    def prepare_author(self, obj):
        if obj.creator:
            return self.get_field_values(obj.creator)

    def prepare_contributors(self, obj):
        if obj.contributor:
            return self.get_field_values(obj.contributor)

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]


    def prepare_link(self, obj):
        electronic_address = []

        urls = [oer.url for oer in OERURL.objects.filter(oer=obj.id)]
        if urls:
            electronic_address.extend(urls)

        attachments = Attachment.objects.filter(object_id=obj.id,
                                                content_type=ContentType.objects.get_for_model(obj))

        for attach in attachments:
            view_url = "%sdocument/view/%s" % (settings.SITE_URL,  attach.short_url)
            electronic_address.append(view_url)

        if electronic_address:
            return electronic_address

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')

    def get_field_values(self, field, attribute = 'text'):
        value_list = field
        if type(field) != list:
            value_list = json.loads(field)

        return [occ.get(attribute) for occ in value_list]

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
