import datetime
from haystack import indexes
from main.models import Resource, Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic


class ResourceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    link = indexes.MultiValueField()
    originator = indexes.MultiValueField()
    author = indexes.MultiValueField()
    source_language = indexes.MultiValueField()
    source_language_display = indexes.MultiValueField()
    source_type = indexes.MultiValueField()
    source_type_display = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()
    abstract = indexes.CharField(model_attr='abstract')
    objective = indexes.CharField(model_attr='objective')
    time_period_textual = indexes.CharField(model_attr='time_period_textual')
    descriptors = indexes.MultiValueField()
    keywords = indexes.MultiValueField()
    status = indexes.IntegerField(model_attr='status')
    created_date = indexes.CharField()

    def get_model(self):
        return Resource

    def prepare_link(self, obj):
        return [line.strip() for line in obj.link.split('\n') if line.strip()]

    def prepare_originator(self, obj):
        return [line.strip() for line in obj.originator.split('\n') if line.strip()]

    def prepare_author(self, obj):
        return [line.strip() for line in obj.author.split('\n') if line.strip()]

    def prepare_source_language(self, obj):
        return [ source_language.acronym for source_language in SourceLanguage.objects.filter(resource=obj.id) ]

    def prepare_source_language_display(self, obj):
        return [ "|".join( source_language.get_translations() ) for source_language in SourceLanguage.objects.filter(resource=obj.id) ]

    def prepare_source_type(self, obj):
        return [ source_type.acronym for source_type in SourceType.objects.filter(resource=obj.id) ]

    def prepare_source_type_display(self, obj):
        return [ "|".join( source_type.get_translations() ) for source_type in SourceType.objects.filter(resource=obj.id) ]

    def prepare_thematic_area(self, obj):
        return [ rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(resource=obj.id) ]

    def prepare_thematic_area_display(self, obj):
        return [ "|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(resource=obj.id) ]

    def prepare_descriptors(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(resource=obj.id, status=1)]

    def prepare_keywords(self, obj):
        return [keyword.text for keyword in Keyword.objects.filter(resource=obj.id, status=1)]

    def prepare_created_date(self, obj):
        return obj.created_time.strftime('%d/%m/%Y')


    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(updated_time__lte=datetime.datetime.now())