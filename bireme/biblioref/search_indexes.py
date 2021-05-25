from django.conf import settings
from haystack import indexes
from haystack.exceptions import SkipDocument
from main.models import Descriptor, Keyword, SourceLanguage, SourceType, ResourceThematic
from biblioref.models import Reference, ReferenceSource, ReferenceAnalytic, ReferenceLocal
from classification.models import Relationship
from attachments.models import Attachment
from title.models import Title
from django.contrib.contenttypes.models import ContentType
from utils.models import AuxCode

import datetime
import json
import re

class ReferenceAnalyticIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    reference_title = indexes.MultiValueField(null=True)
    author = indexes.MultiValueField(null=True)
    reference_abstract = indexes.MultiValueField()
    abstract_language = indexes.MultiValueField()
    reference_source = indexes.CharField()
    link = indexes.MultiValueField()
    publication_type = indexes.CharField()
    indexed_database = indexes.MultiValueField()
    database = indexes.MultiValueField()
    publication_language = indexes.MultiValueField()
    publication_date = indexes.CharField()
    publication_year = indexes.CharField()
    publication_country = indexes.CharField()
    journal = indexes.CharField()

    mj = indexes.MultiValueField()
    mh = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()

    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return ReferenceAnalytic


    def prepare(self, obj):
        self.prepared_data = super(ReferenceAnalyticIndex, self).prepare(obj)

        # create dynamic filters for collections
        c_type = ContentType.objects.get_for_model(Reference)
        relation_list = Relationship.objects.filter(object_id=obj.id, content_type=c_type).all()

        if relation_list:
            collection_filter = {}
            for rel in relation_list:
                collection_parent_slug = [parent.slug for parent in rel.collection.get_parents()]
                # filter_id is created using the slug of parents "e-blueinfo_ops-guid"
                filter_id = "_".join(collection_parent_slug)

                collection_filter_item = "|".join(rel.collection.get_translations())
                if not filter_id in collection_filter:
                    collection_filter[filter_id] = []

                collection_filter[filter_id].append(collection_filter_item)

            # populate haystack prepared_data to send to solr
            for filter_name, filter_value in collection_filter.items():
                # add prefix filter_ to match dynamic field definition in schema.xml
                filter_name = "collection_%s" % filter_name
                self.prepared_data[filter_name] = filter_value


        return self.prepared_data


    def prepare_reference_title(self, obj):
        if obj.title:
            return self.get_field_values(obj.title)

    def prepare_author(self, obj):
        if obj.individual_author:
            return self.get_field_values(obj.individual_author)

    def prepare_link(self, obj):
        electronic_address = []
        if obj.electronic_address:
            electronic_address = self.get_field_values(obj.electronic_address, '_u')

        attachments = Attachment.objects.filter(object_id=obj.id,
                                                content_type=ContentType.objects.get_for_model(obj))

        for attach in attachments:
            view_url = "%sdocument/view/%s" % (settings.SITE_URL,  attach.short_url)
            electronic_address.append(view_url)

        if electronic_address:
            return electronic_address

    def prepare_reference_abstract(self, obj):
        if obj.abstract:
            return self.get_field_values(obj.abstract)

    def prepare_abstract_language(self, obj):
        # export a field with language identification (pt, es, en) and abstract text separate by pipe |
        if obj.abstract:
            ab_list = obj.abstract
            ab_lang = list()
            if type(ab_list) != list:
                ab_list = json.loads(obj.abstract)

            for ab in ab_list:
                 ab_lang.append(u"{}|{}".format(ab.get('_i'), ab.get('text')))

            return ab_lang

    def prepare_reference_source(self, obj):
        source = u"{0}; {1} ({2}), {3}".format(obj.source.title_serial,
                                               obj.source.volume_serial,
                                               obj.source.issue_number,
                                               obj.source.publication_date_normalized[:4])
        return source

    def prepare_publication_language(self, obj):
        lang_list = []
        if obj.text_language:
            for code in obj.text_language:
                aux_code = AuxCode.objects.get(field='text_language', code=code)
                lang_translations = "|".join(aux_code.get_translations())
                lang_list.append(lang_translations)

            return lang_list

    def prepare_indexed_database(self, obj):
        return [occ.acronym for occ in obj.indexed_database.all()]

    def prepare_database(self, obj):
        db_list = []
        library_records = ReferenceLocal.objects.filter(source=obj.id)
        if library_records:
            for library in library_records:
                local_db_list = [line.strip() for line in library.database.split('\r\n') if line.strip()]
                db_list.extend(local_db_list)

        return [occ for occ in db_list]

    def prepare_journal(self, obj):
        return obj.source.title_serial

    def prepare_publication_type(self, obj):
        literature_type = re.sub('[CP]', '', obj.literature_type)
        return literature_type

    def prepare_publication_date(self, obj):
        return obj.source.publication_date_normalized

    def prepare_publication_year(self, obj):
        return obj.source.publication_date_normalized[:4]

    def prepare_publication_country(self, obj):
        if obj.source:
            title = Title.objects.filter(shortened_title=obj.source.title_serial).first()
            if title:
                country_list = []
                for country in title.country.all():
                    country_translations = "|".join(country.get_translations())
                    country_list.append(country_translations)

                return country_list

    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thematic_area_display(self, obj):
        return ["|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_mj(self, obj):
        # used for filter / populate with primary descriptors
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), primary=True)]

    def prepare_mh(self, obj):
        # used for search and record presentation / populate with all descriptors (mh)
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
    abstract_language = indexes.MultiValueField()
    link = indexes.MultiValueField()
    publication_type = indexes.CharField()
    indexed_database = indexes.MultiValueField()
    database = indexes.MultiValueField()
    publication_language = indexes.MultiValueField()
    publication_date = indexes.CharField()
    publication_year = indexes.CharField()
    publication_country = indexes.CharField()

    mj = indexes.MultiValueField()
    mh = indexes.MultiValueField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()

    created_date = indexes.CharField()
    updated_date = indexes.CharField()
    status = indexes.IntegerField(model_attr='status')

    thesis_dissertation_leader = indexes.CharField()
    thesis_dissertation_institution = indexes.CharField(model_attr='thesis_dissertation_institution')
    thesis_dissertation_academic_title = indexes.CharField(model_attr='thesis_dissertation_academic_title')

    def get_model(self):
        return ReferenceSource


    def prepare(self, obj):
        self.prepared_data = super(RefereceSourceIndex, self).prepare(obj)

        # create dynamic filters for collections
        c_type = ContentType.objects.get_for_model(Reference)
        relation_list = Relationship.objects.filter(object_id=obj.id, content_type=c_type).all()

        if relation_list:
            collection_filter = {}
            for rel in relation_list:
                collection_parent_slug = [parent.slug for parent in rel.collection.get_parents()]
                # filter_id is created using the slug of parents "e-blueinfo_ops-guid"
                filter_id = "_".join(collection_parent_slug)

                collection_filter_item = "|".join(rel.collection.get_translations())
                if not filter_id in collection_filter:
                    collection_filter[filter_id] = []

                collection_filter[filter_id].append(collection_filter_item)

            # populate haystack prepared_data to send to solr
            for filter_name, filter_value in collection_filter.items():
                # add prefix filter_ to match dynamic field definition in schema.xml
                filter_name = "collection_%s" % filter_name
                self.prepared_data[filter_name] = filter_value


        return self.prepared_data


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
        electronic_address = []
        if obj.electronic_address:
            electronic_address = self.get_field_values(obj.electronic_address, '_u')

        attachments = Attachment.objects.filter(object_id=obj.id,
                                                content_type=ContentType.objects.get_for_model(obj))

        for attach in attachments:
            view_url = "%sdocument/view/%s" % (settings.SITE_URL,  attach.short_url)
            electronic_address.append(view_url)

        if electronic_address:
            return electronic_address

    def prepare_reference_abstract(self, obj):
        if obj.abstract:
            return self.get_field_values(obj.abstract)

    def prepare_abstract_language(self, obj):
        # export a field with language identification (pt, es, en) and abstract text separate by pipe |
        if obj.abstract:
            ab_list = obj.abstract
            ab_lang = list()
            if type(ab_list) != list:
                ab_list = json.loads(obj.abstract)

            for ab in ab_list:
                 ab_lang.append(u"{}|{}".format(ab.get('_i'), ab.get('text')))

            return ab_lang

    def prepare_publication_language(self, obj):
        lang_list = []
        if obj.text_language:
            for code in obj.text_language:
                aux_code = AuxCode.objects.get(field='text_language', code=code)
                lang_translations = "|".join(aux_code.get_translations())
                lang_list.append(lang_translations)

            return lang_list

    def prepare_indexed_database(self, obj):
        return [occ.acronym for occ in obj.indexed_database.all()]

    def prepare_database(self, obj):
        db_list = []
        library_records = ReferenceLocal.objects.filter(source=obj.id)
        if library_records:
            for library in library_records:
                local_db_list = [line.strip() for line in library.database.split('\r\n') if line.strip()]
                db_list.extend(local_db_list)

        return [occ for occ in db_list]

    def prepare_publication_type(self, obj):
        # avoid indexing article source (onyl analytics)
        if obj.literature_type[0] == 'S':
            raise SkipDocument

        literature_type = re.sub('[CP]', '', obj.literature_type)
        return literature_type

    def prepare_publication_country(self, obj):
        if obj.publication_country:
            return ["|".join(obj.publication_country.get_translations())]

    def prepare_publication_date(self, obj):
        return obj.publication_date_normalized

    def prepare_publication_year(self, obj):
        return obj.publication_date_normalized[:4]

    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thematic_area_display(self, obj):
        return ["|".join( rt.thematic_area.get_translations() ) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_mj(self, obj):
        # used for filter / populate with primary descriptors
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), primary=True)]

    def prepare_mh(self, obj):
        # used for search and record presentation / populate with all descriptors (mh)
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))]

    def prepare_thesis_dissertation_leader(self, obj):
        if obj.thesis_dissertation_leader:
            return self.get_field_values(obj.thesis_dissertation_leader)

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
