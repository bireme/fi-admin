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
    medline_shortened_title = indexes.CharField(model_attr='medline_shortened_title')
    section = indexes.CharField(model_attr='section')
    section_title = indexes.CharField(model_attr='section_title')
    initial_volume = indexes.CharField(model_attr='initial_volume')
    final_volume = indexes.CharField(model_attr='final_volume')
    initial_number = indexes.CharField(model_attr='initial_number')
    final_number = indexes.CharField(model_attr='final_number')
    initial_date = indexes.CharField(model_attr='initial_date')
    final_date = indexes.CharField(model_attr='final_date')
    responsibility_mention = indexes.CharField(model_attr='responsibility_mention')
    issn = indexes.CharField(model_attr='issn')
    thematic_area = indexes.MultiValueField()
    descriptor = indexes.MultiValueField()
    keyword = indexes.MultiValueField()
    country = indexes.MultiValueField()
    city = indexes.CharField(model_attr='city')
    language = indexes.MultiValueField()
    status = indexes.CharField()
    created_date = indexes.CharField()
    updated_date = indexes.CharField()

    def get_model(self):
        return Title

    def get_updated_field(self):
        return "updated_time"

    def prepare_status(self, obj):
        if obj.status == '?':
            raise SkipDocument
        else:
            status_int = 1 if obj.status == 'C' else 0
            return status_int

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_keyword(self, obj):
        return [keyword.text for keyword in Keyword.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_country(self, obj):
        if obj.country:
            country_list = []
            for country in obj.country.all():
                country_translations = "|".join(country.get_translations())
                country_list.append(country_translations)

            return country_list

    def prepare_thematic_area(self, obj):
        return [line.strip() for line in obj.thematic_area.split('\n') if line.strip()]

    def prepare_language(self, obj):
        if obj.text_language:
            translations = ["|".join(text_language.get_translations()) for text_language in obj.text_language.all()]
            return translations

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())

