import datetime
from haystack import indexes
from haystack.exceptions import SkipDocument
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from title.models import Title

from django.contrib.contenttypes.models import ContentType

class TitleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    subtitle = indexes.CharField(model_attr='subtitle')
    shortened_title = indexes.CharField(model_attr='shortened_title')
    issn = indexes.CharField(model_attr='issn')
    thematic_area = indexes.MultiValueField()
    status = indexes.CharField(model_attr='status')
    descriptor = indexes.MultiValueField()
    keyword = indexes.MultiValueField()
    country = indexes.CharField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()

    def get_model(self):
        return Title

    def get_updated_field(self):
        return "updated_time"

    def prepare_status(self, obj):
        if obj.status == 'C':
            return 1
        else:
            raise SkipDocument

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_keyword(self, obj):
        return [keyword.text for keyword in Keyword.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_country(self, obj):
        if obj.country:
            translations = obj.country.get_translations()
            return "|".join(translations)

    def prepare_thematic_area(self, obj):
        return [line.strip() for line in obj.thematic_area.split('\n') if line.strip()]

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())

