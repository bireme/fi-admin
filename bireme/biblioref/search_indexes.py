import datetime
import json
from haystack import indexes
from haystack.exceptions import SkipDocument
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from biblioref.models import Reference, ReferenceSource, ReferenceAnalytic

from django.contrib.contenttypes.models import ContentType


class ReferenceAnalyticIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    reference_title = indexes.MultiValueField(null=True)
    author = indexes.MultiValueField(null=True)
    reference_abstract = indexes.MultiValueField()
    reference_source = indexes.CharField()
    link = indexes.MultiValueField()
    publication_type = indexes.CharField()
    database = indexes.MultiValueField()
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
        if obj.title:
            return self.get_field_values(obj.title)

    def prepare_author(self, obj):
        if obj.individual_author:
            return self.get_field_values(obj.individual_author)

    def prepare_link(self, obj):
        if obj.electronic_address:
            return self.get_field_values(obj.electronic_address, '_u')

    def prepare_reference_abstract(self, obj):
        if obj.abstract:
            return self.get_field_values(obj.abstract)

    def prepare_reference_source(self, obj):
        source = u"{0}; {1} ({2}), {3}".format(obj.source.title_serial,
                                               obj.source.volume_serial,
                                               obj.source.issue_number,
                                               obj.source.publication_date_normalized[:4])
        return source

    def prepare_publication_language(self, obj):
        if obj.text_language:
            return [occ for occ in obj.text_language]

    def prepare_database(self, obj):
        return [occ for occ in obj.indexed_database.all()]

    def prepare_journal(self, obj):
        return obj.source.title_serial

    def prepare_publication_type(self, obj):
        publication_type = ''
        if obj.literature_type[0] == 'S':
            publication_type = 'article'

        return publication_type

    def prepare_publication_year(self, obj):
        return obj.source.publication_date_normalized[:4]

    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thematic_area_display(self, obj):
        return ["|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

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


class RefereceSourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    reference_title = indexes.MultiValueField(null=True)
    author = indexes.MultiValueField(null=True)
    reference_abstract = indexes.MultiValueField()
    link = indexes.MultiValueField()
    publication_type = indexes.CharField()
    database = indexes.MultiValueField()
    publication_language = indexes.MultiValueField()
    publication_year = indexes.CharField()

    descriptor = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()

    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return ReferenceSource

    def prepare_reference_title(self, obj):
        title = ''
        if obj.title_monographic:
            title = self.get_field_values(obj.title_monographic)
        elif obj.title_collection:
            title = self.get_field_values(obj.title_collection)

        return title

    def prepare_author(self, obj):
        author_list = []
        if obj.individual_author_monographic:
            author_list = self.get_field_values(obj.individual_author_monographic)
        elif obj.corporate_author_monographic:
            author_list = self.get_field_values(obj.corporate_author_monographic)
        elif obj.individual_author_collection:
            author_list = self.get_field_values(obj.individual_author_collection)
        elif obj.corporate_author_collection:
            author_list = self.get_field_values(obj.corporate_author_collection)

        return author_list

    def prepare_link(self, obj):
        if obj.electronic_address:
            return self.get_field_values(obj.electronic_address, '_u')

    def prepare_reference_abstract(self, obj):
        if obj.abstract:
            return self.get_field_values(obj.abstract)

    def prepare_publication_language(self, obj):
        if obj.text_language:
            return [occ for occ in obj.text_language]

    def prepare_database(self, obj):
        return [occ for occ in obj.indexed_database.all()]

    def prepare_publication_type(self, obj):
        publication_type = ''
        # avoid indexing article source (onyl analytics)
        if obj.literature_type[0] == 'S':
            raise SkipDocument

        if obj.literature_type[0] == 'T':
            publication_type = 'thesis'
        elif obj.literature_type[0] == 'M':
            publication_type = 'monographic'

        return publication_type

    def prepare_publication_year(self, obj):
        return obj.publication_date_normalized[:4]

    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thematic_area_display(self, obj):
        return ["|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

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
