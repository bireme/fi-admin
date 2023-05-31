import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from multimedia.models import Media, MediaType

from django.contrib.contenttypes.models import ContentType

class MediaIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    title_translated = indexes.CharField(model_attr='title_translated')
    link = indexes.CharField(model_attr='link', null=True)
    description = indexes.CharField(model_attr='description', null=True)
    authors = indexes.MultiValueField()
    contributors = indexes.MultiValueField()
    related_links = indexes.MultiValueField()
    media_collection = indexes.CharField(model_attr='media_collection', null=True)
    item_extension = indexes.CharField(model_attr='item_extension', null=True)
    other_physical_details = indexes.CharField(model_attr='other_physical_details', null=True)
    dimension = indexes.CharField(model_attr='dimension', null=True)
    publisher = indexes.CharField(model_attr='publisher', null=True)
    content_notes = indexes.CharField(model_attr='content_notes', null=True)
    version_notes = indexes.CharField(model_attr='version_notes', null=True)
    publication_date = indexes.CharField(model_attr='publication_date', null=True)
    language = indexes.MultiValueField()
    language_display = indexes.MultiValueField()
    media_type = indexes.MultiValueField()
    media_type_filter = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()
    descriptor = indexes.MultiValueField()
    keyword = indexes.MultiValueField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return Media

    '''
    def should_update(self, instance, **kwargs):
        if instance.status != 0:
            return True

        return False
    '''

    def prepare_media_type(self, obj):
        return [ media_type.acronym for media_type in MediaType.objects.filter(media=obj.id) ]

    def prepare_media_type_filter(self, obj):
        return [ "|".join( media_type.get_translations() ) for media_type in MediaType.objects.filter(media=obj.id) ]

    def prepare_language(self, obj):
        return [ source_language.acronym for source_language in SourceLanguage.objects.filter(media=obj.id) ]

    def prepare_language_display(self, obj):
        return [ "|".join( source_language.get_translations() ) for source_language in SourceLanguage.objects.filter(media=obj.id) ]

    def prepare_authors(self, obj):
        return [line.strip() for line in obj.authors.split('\n') if line.strip()]

    def prepare_contributors(self, obj):
        return [line.strip() for line in obj.contributors.split('\n') if line.strip()]

    def prepare_related_links(self, obj):
        return [line.strip() for line in obj.related_links.split('\n') if line.strip()]

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
    def prepare_media_type(self, obj):
        return [ "|".join( event_type.get_translations() ) for event_type in EventType.objects.filter(event=obj.id) ]


'''