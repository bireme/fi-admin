import datetime
from haystack import indexes
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from biblioref.models import Reference, ReferenceSource, ReferenceAnalytic

from django.contrib.contenttypes.models import ContentType

class RefereceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    reference_title = indexes.MultiValueField(model_attr='title', null=True)
    reference_abstract = indexes.MultiValueField(model_attr='abstract', null=True)
    reference_source = indexes.CharField()
    author = indexes.MultiValueField(model_attr='individual_author', null=True)
    link = indexes.MultiValueField(model_attr='electronic_address', null=True)
    publication_type = indexes.CharField()
    # database = indexes.MultiValueField()
    publication_language = indexes.MultiValueField()
    publication_year = indexes.CharField()
    journal = indexes.CharField()

    descriptor = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()

    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return ReferenceAnalytic

    def prepare_reference_title(self, obj):
        return [occ['text'] for occ in obj.title]

    def prepare_author(self, obj):
        if obj.individual_author:
            return [occ['text'] for occ in obj.individual_author]

    def prepare_link(self, obj):
        if obj.electronic_address:
            return [occ['_u'] for occ in obj.electronic_address]

    def prepare_reference_abstract(self, obj):
        if obj.abstract and type(obj.abstract) == list:
            return [occ['text'] for occ in obj.abstract]

    def prepare_reference_source(self, obj):
        source = u"{0}; {1} ({2}), {3}".format(obj.source.title_serial,
                                               obj.source.volume_serial,
                                               obj.source.issue_number,
                                               obj.source.publication_date_normalized[:4])
        return source

    def prepare_publication_language(self, obj):
        return [occ for occ in obj.text_language]

    def prepare_database(self, obj):
        return [line.strip() for line in obj.database.split('\n') if line.strip()]

    def prepare_journal(self, obj):
        return obj.source.title_serial

    def prepare_publication_type(self, obj):
        publication_type = ''
        if obj.literature_type == 'S':
            publication_type = 'article'

        return publication_type

    def prepare_publication_year(self, obj):
        return obj.source.publication_date_normalized[:4]


    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thematic_area_display(self, obj):
        return ["|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')



    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
