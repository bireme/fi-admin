import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from events.models import Event, EventType

from django.contrib.contenttypes.models import ContentType


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    link = indexes.CharField(model_attr='link', null=True)
    address = indexes.CharField(model_attr='address', null=True)
    city = indexes.CharField(model_attr='city', null=True)
    country = indexes.CharField(model_attr='country', null=True)
    start_date = indexes.DateTimeField(model_attr='start_date')
    end_date = indexes.DateTimeField(model_attr='end_date')
    contact_email = indexes.CharField(model_attr='contact_email', null=True)
    contact_info = indexes.CharField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()
    official_language = indexes.MultiValueField()
    official_language_display = indexes.MultiValueField()
    event_modality = indexes.CharField()
    event_type = indexes.MultiValueField()
    descriptor = indexes.MultiValueField()
    keyword = indexes.MultiValueField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')
    not_regional_event = indexes.CharField(model_attr='not_regional_event')
    observations = indexes.CharField()
    target_groups = indexes.CharField()

    def get_model(self):
        return Event

    def prepare_official_language(self, obj):
        return [ source_language.acronym for source_language in SourceLanguage.objects.filter(event=obj.id) ]

    def prepare_official_language_display(self, obj):
        return [ "|".join( source_language.get_translations() ) for source_language in SourceLanguage.objects.filter(event=obj.id) ]

    def prepare_event_type(self, obj):
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
