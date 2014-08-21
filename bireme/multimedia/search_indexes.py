import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from models import Media, MediaType

from django.contrib.contenttypes.models import ContentType

'''    
class MediaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    url = indexes.CharField(model_attr='url', null=True)
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()
    #media_type = indexes.MultiValueField()
    descriptor = indexes.MultiValueField()
    keyword = indexes.MultiValueField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return Media

    def prepare_media_type(self, obj):
        return [ "|".join( event_type.get_translations() ) for event_type in EventType.objects.filter(event=obj.id) ]

    def prepare_thematic_area(self, obj):
        return [ rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj)) ]

    def prepare_thematic_area_display(self, obj):
        return [ "|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj)) ]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_keyword(self, obj):
        return [keyword.text for keyword in Keyword.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]


    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')


    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
'''