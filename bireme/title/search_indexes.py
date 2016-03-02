import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, SourceType
from models import Title

from django.contrib.contenttypes.models import ContentType

class TitleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    descriptor = indexes.MultiValueField()
    #keyword = indexes.MultiValueField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return Title

    # def should_update(self, instance, **kwargs):
    #     if instance.status != 0:
    #         return True
    #
    #     return False

    def prepare_title(self, obj):
        return [occ['text'] for occ in obj.title]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    # def prepare_keyword(self, obj):
    #     return [keyword.text for keyword in Keyword.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
