import datetime
from haystack import indexes
from main.models import Descriptor, ResourceThematic
from models import *
from attachments.models import Attachment
from django.conf import settings

from django.contrib.contenttypes.models import ContentType


class LeisRefIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    title = indexes.CharField(model_attr='title')
    status = indexes.IntegerField(model_attr='status')
    scope_region = indexes.CharField()
    act_type = indexes.CharField()
    act_number = indexes.CharField(model_attr='act_number')
    scope = indexes.CharField()
    scope_state = indexes.CharField()
    scope_city = indexes.CharField()
    source_name = indexes.CharField()
    indexed_database = indexes.MultiValueField()
    collection = indexes.MultiValueField()
    denomination = indexes.CharField(model_attr='denomination')
    issue_date = indexes.CharField(model_attr='issue_date', default='')
    publication_date = indexes.CharField(model_attr='publication_date', default='')
    publication_year = indexes.CharField()
    organ_issuer = indexes.CharField()
    language = indexes.CharField()
    official_ementa = indexes.CharField(model_attr='official_ementa')
    unofficial_ementa = indexes.CharField(model_attr='unofficial_ementa')
    relationship_active = indexes.CharField()
    relationship_passive = indexes.CharField()
    thematic_area = indexes.MultiValueField()
    thematic_area_display = indexes.MultiValueField()
    fulltext = indexes.MultiValueField()
    created_date = indexes.CharField()
    descriptor = indexes.MultiValueField()
    updated_date = indexes.CharField()

    def get_model(self):
        return Act

    def prepare_scope_region(self, obj):
        if obj.scope_region:
            translations = obj.scope_region.get_translations()
            return "|".join(translations)

    def prepare_act_type(self, obj):
        if obj.act_type:
            translations = obj.act_type.get_translations()
            return "|".join(translations)

    def prepare_scope(self, obj):
        if obj.scope:
            translations = obj.scope.get_translations()
            return "|".join(translations)

    def prepare_source_name(self, obj):
        if obj.source_name:
            translations = obj.source_name.get_translations()
            return "|".join(translations)

    def prepare_organ_issuer(self, obj):
        if obj.organ_issuer:
            translations = obj.organ_issuer.get_translations()
            return "|".join(translations)

    def prepare_scope_state(self, obj):
        if obj.scope_state:
            translations = obj.scope_state.get_translations()
            return "|".join(translations)

    def prepare_scope_city(self, obj):
        if obj.scope_city:
            translations = obj.scope_city.get_translations()
            return "|".join(translations)

    def prepare_language(self, obj):
        if obj.language:
            translations = obj.language.get_translations()
            return "|".join(translations)

    def prepare_collection(self, obj):
        if obj.act_collection:
            translations = obj.act_collection.get_translations()
            return "|".join(translations)

    def prepare_indexed_database(self, obj):
        return [occ.acronym for occ in obj.indexed_database.all()]

    def prepare_publication_year(self, obj):
        if obj.issue_date:
            return obj.issue_date.strftime("%Y")

    def prepare_relationship_active(self, obj):
        active_relationships = []
        act_list = ActRelationship.objects.filter(act_related=obj.pk)
        for act in act_list:
            label_present = "|".join(act.relation_type.get_label_present_translations())
            ref_type = "|".join(act.act_referred.act_type.get_translations())
            ref_number = act.act_referred.act_number
            ref_date = act.act_referred.issue_date
            ref_lnk = "leisref.act.{0}".format(act.act_referred.id) if act.act_referred.status in [-2, 1] else ''
            active_relation = u"{0}@{1}@{2}@{3}@{4}@{5}".format(label_present, ref_type, ref_number,
                                                               ref_date, act.act_apparatus, ref_lnk)
            active_relationships.append(active_relation)

        return active_relationships

    def prepare_relationship_passive(self, obj):
        passive_relationships = []
        act_list = ActRelationship.objects.filter(act_referred=obj.pk)
        for act in act_list:
            label_past = "|".join(act.relation_type.get_label_past_translations())
            act_type = "|".join(obj.act_type.get_translations())
            ref_lnk = "leisref.act.{0}".format(act.act_related.id) if act.act_related.status in [-2, 1] else ''
            passive_relation = u"{0}@{1}@{2}@{3}@{4}".format(label_past, act_type, act.act_related.act_number,
                                                            act.act_related.issue_date, ref_lnk)
            passive_relationships.append(passive_relation)

        return passive_relationships

    def prepare_thematic_area(self, obj):
        return [rt.thematic_area.acronym for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj)) ]

    def prepare_thematic_area_display(self, obj):
        return ["|".join(rt.thematic_area.get_translations()) for rt in ResourceThematic.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj)) ]

    def prepare_descriptor(self, obj):
        return [descriptor.code for descriptor in Descriptor.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj), status=1)]

    def prepare_fulltext(self, obj):
        c_type = ContentType.objects.get_for_model(obj)

        view_attachement_url = "{0}document/view/".format(settings.SITE_URL)

        url_list = ["{0}|{1}".format(u.language, u.url) for u in ActURL.objects.filter(act=obj)]
        att_list = ["{0}|{1}".format(a.language, "{0}{1}".format(view_attachement_url, a.short_url)) for a in Attachment.objects.filter(object_id=obj.id, content_type=c_type)]

        url_list.extend(att_list)

        return url_list

    def prepare_created_date(self, obj):
        if obj.created_time:
            return obj.created_time.strftime('%Y%m%d')

    def prepare_updated_date(self, obj):
        if obj.updated_time:
            return obj.updated_time.strftime('%Y%m%d')

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_time__lte=datetime.datetime.now())
