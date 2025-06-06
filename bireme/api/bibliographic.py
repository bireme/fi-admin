# coding: utf-8
from django.conf import settings
from django.urls import re_path
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields

from biblioref.models import Reference, ReferenceSource, ReferenceAnalytic, ReferenceAlternateID, ReferenceLocal, ReferenceComplement
from attachments.models import Attachment
from related.models import LinkedResource, LinkedResearchData
from api.isis_serializer import ISISSerializer
from api.tastypie_custom import CustomResource

from main.models import Descriptor, ResourceThematic
from database.models import Database
from biblioref.field_definitions import field_tag_map
from copy import copy

import os
import requests
import urllib
import json


class ReferenceResource(CustomResource):
    class Meta:
        queryset = Reference.objects.prefetch_related('indexed_database', 'created_by', 'updated_by').all()
        allowed_methods = ['get']
        serializer = ISISSerializer(formats=['json', 'xml', 'isis_id'], field_tag=field_tag_map)
        resource_name = 'bibliographic'
        filtering = {
            'updated_time': ('gte', 'lte'),
            'status': 'exact',
            'LILACS_original_id': ALL,
            'indexed_database': ALL,
            'collection': ALL,
            'id': ALL
        }
        include_resource_uri = True
        max_limit = settings.MAX_EXPORT_API_LIMIT


    def build_filters(self, filters=None, *args, **kwargs):
        orm_filters = super(ReferenceResource, self).build_filters(filters, *args, **kwargs)

        if 'indexed_database' in filters:
            filter_db = filters['indexed_database']
            filter_db_id = Database.objects.get(acronym=filter_db)
            orm_filters['indexed_database__exact'] = filter_db_id

        if 'collection' in filters:
            filter_col_id = filters['collection']
            orm_filters['collection__collection_id'] = filter_col_id

        return orm_filters

    def prepend_urls(self):
        return [
            re_path(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_search'), name="api_get_search"),
            re_path(r"^(?P<resource_name>%s)/get_last_id%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_last_id'), name="api_get_last_id"),
        ]

    def get_search(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        q = request.GET.get('q', '')
        fq = request.GET.get('fq', '')
        fb = request.GET.get('fb', '')
        start = request.GET.get('start', 0)
        count = request.GET.get('count', 0)
        lang = request.GET.get('lang', 'pt')
        op = request.GET.get('op', 'search')
        id = request.GET.get('id', '')
        sort = request.GET.get('sort', 'publication_date desc')
        facet_list = request.GET.getlist('facet.field', [])

        # filter result by status = -3 (Migration) OR 0 (LILACS Express) OR 1 (published)
        if fq != '':
            fq = '(status:("-3" OR "0" OR "1") AND django_ct:biblioref.reference*) AND %s' % fq
        else:
            fq = '(status:("-3" OR "0" OR "1") AND django_ct:biblioref.reference*)'

        if id != '':
            q = 'id:%s' % id

        # url
        search_url = "%s/search_json" % settings.SEARCH_SERVICE_URL

        search_params = {'site': settings.SEARCH_INDEX, 'op': op, 'output': 'site', 'lang': lang,
                         'q': q, 'fq': [fq], 'fb': fb, 'start': int(start), 'count': int(count), 'sort': sort}

        if facet_list:
            search_params['facet.field'] = []
            for facet_field in facet_list:
                search_params['facet.field'].append(facet_field)
                facet_limit_param = 'f.{}.facet.limit'.format(facet_field)
                facet_field_limit = request.GET.get(facet_limit_param, None)
                if facet_field_limit:
                    search_params[facet_limit_param] = facet_field_limit

        search_params_json = json.dumps(search_params)
        request_headers = {'apikey': settings.SEARCH_SERVICE_APIKEY}

        r = requests.post(search_url, data=search_params_json, headers=request_headers)
        try:
            response_json = r.json()
        except ValueError:
            response_json = json.loads('{"type": "error", "message": "invalid output"}')

        # Duplicate "response" to "match" element for old compatibility calls
        if id != '' and response_json:
            response_json['diaServerResponse'][0]['match'] = response_json['diaServerResponse'][0]['response']


        self.log_throttled_access(request)
        return self.create_response(request, response_json)

    def full_dehydrate(self, bundle, for_list=False):
        # complete bundle fields with child fields. Ex. Analytic and Source fields to Reference

        # first populate bundle with Reference fields
        bundle = super(ReferenceResource, self).full_dehydrate(bundle)

        # Check type of Reference to add additional fields to bundle
        reference_id = bundle.obj.id
        if 'a' in bundle.data['treatment_level']:
            obj = ReferenceAnalytic.objects.get(pk=reference_id)
        else:
            obj = ReferenceSource.objects.get(pk=reference_id)

        # Add additional fields to bundle
        bundle = self.add_fields_to_bundle(bundle, obj)

        # Add Source fields to bundle
        if 'source' in bundle.data:
            import_field_list = ['title_serial', 'volume_serial', 'issue_number', 'issn',
                                 'publication_date', 'publication_date_normalized',
                                 'individual_author_monographic', 'corporate_author_monographic',
                                 'title_monographic', 'english_title_monographic', 'pages_monographic',
                                 'volume_monographic', 'publisher', 'edition', 'publication_city',
                                 'publication_country', 'symbol', 'isbn', 'individual_author_collection',
                                 'corporate_author_collection', 'title_collection', 'english_title_collection',
                                 'total_number_of_volumes', 'thesis_dissertation_leader',
                                 'thesis_dissertation_institution', 'thesis_dissertation_academic_title', 'license']

            source_id = bundle.data['source']
            obj_source = ReferenceSource.objects.get(pk=source_id)
            bundle = self.add_fields_to_bundle(bundle, obj_source, import_field_list)
            bundle.data['source_control'] = 'FONTE'

        # Add system version control number
        version_file = open(os.path.join(settings.BASE_DIR, 'templates/version.txt'))
        version_number = version_file.readlines()[0]
        bundle.data['system_version'] = version_number.rstrip()

        return bundle

    def add_fields_to_bundle(self, bundle, obj, import_field_list=[]):
        for field in obj._meta.get_fields():
            field_value = getattr(obj, field.name, {})

            # check if field has multiples values (ex. ManyToManyField)
            if hasattr(field_value, 'all'):
                # if field is empty skip to next field
                if not field_value.all().exists():
                    continue

            if field_value:
                # if import_field_list is present check if field is the list
                if import_field_list:
                    if field.name in import_field_list:
                        bundle.data[field.name] = copy(field_value)
                # check if field is not already in bundle or has no value in bundle.data
                elif field.name not in bundle.data or not bundle.data.get(field.name):
                    bundle.data[field.name] = copy(field_value)

        return bundle

    def dehydrate(self, bundle):
        # retrive child class of reference (analytic or source) for use in ContentType query
        child_class = bundle.obj.child_class()
        c_type = ContentType.objects.get_for_model(child_class)

        descriptors = Descriptor.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)
        thematic_areas = ResourceThematic.objects.filter(object_id=bundle.obj.id, content_type=c_type, status=1)
        attachments = Attachment.objects.filter(object_id=bundle.obj.id, content_type=c_type)
        alternate_ids = ReferenceAlternateID.objects.filter(reference_id=bundle.obj.id)
        library_records = ReferenceLocal.objects.filter(source=bundle.obj.id)
        complement_data = ReferenceComplement.objects.filter(source=bundle.obj.id)
        related_obj_id = 'biblio-{}'.format(bundle.obj.id)
        related_resources = LinkedResource.objects.filter( Q(object_id=bundle.obj.id, content_type=c_type) | Q(internal_id=related_obj_id) )
        related_research = LinkedResearchData.objects.filter(object_id=bundle.obj.id, content_type=c_type)

        # create lists for primary and secundary descriptors
        descriptors_primary = []
        descriptors_secundary = []
        for descriptor in descriptors:
            # use text field when code not set (migration records of old DeCS terms)
            if descriptor.code:
                descriptor_data = {'text': descriptor.code}
            else:
                descriptor_data = {'text': u'^d{0}'.format(descriptor.text)}

            if descriptor.primary:
                descriptors_primary.append(descriptor_data)
            else:
                descriptors_secundary.append(descriptor_data)

        # add fields to output
        bundle.data['MFN'] = bundle.obj.id
        bundle.data['descriptors_primary'] = descriptors_primary
        bundle.data['descriptors_secondary'] = descriptors_secundary
        bundle.data['thematic_areas'] = [{'text': thematic.thematic_area.name} for thematic in thematic_areas]
        bundle.data['alternate_ids'] = [alt.alternate_id for alt in alternate_ids]
        indexed_database_list = bundle.obj.indexed_database.all()
        bundle.data['indexed_database'] = [database.acronym for database in indexed_database_list]

        # add related resource
        related_resource_list = []
        for related in related_resources:
            if related.object_id == bundle.obj.id:
                related_dict = {"_i": related.type.field, "_t": related.title, "_6": related.link, "_w": related.internal_id}
                related_dict_json = self.dict2json(related_dict)
                related_resource_list.append(related_dict_json)
            else:
                related_id = 'biblio-{}'.format(related.object_id)
                related_title = Reference.objects.get(pk=related.object_id).reference_title
                related_dict = {"_i": related.type.field_passive.field, "_t": related_title, "_6": related.link, "_w": related_id}
                related_dict_json = self.dict2json(related_dict)
                related_resource_list.append(related_dict_json)

        bundle.data['related_resource'] = related_resource_list

        # add related research
        related_research_list = []
        for research in related_research:
            research_dict = {"_t": research.title, "_6": research.link, "_n": research.description}
            research_dict_json = self.dict2json(research_dict)
            related_research_list.append(research_dict_json)

        bundle.data['related_research'] = related_research_list

        # check if object has classification (relationship model)
        if bundle.obj.collection.count():
            community_list = []
            collection_list = []
            community_collection_path = []

            collection_all = bundle.obj.collection.all()
            for rel in collection_all:
                collection_labels = "|".join(rel.collection.get_translations())
                collection_item = u"{}|{}".format(rel.collection.id, collection_labels)
                collection_list.append(collection_item)
                community_collection_path.append(rel.collection.community_collection_path_translations())

                if rel.collection.parent:
                    community_labels = "|".join(rel.collection.parent.get_translations())
                    community_item = u"{}|{}".format(rel.collection.parent.id, community_labels)
                    community_list.append(community_item)

            bundle.data['community'] = community_list
            bundle.data['collection'] = collection_list
            bundle.data['community_collection_path'] = community_collection_path

        # change code of cooperative_center_code to indexer_cc_code at API record export #553
        if bundle.obj.indexer_cc_code:
            bundle.data['cooperative_center_code'] = bundle.obj.indexer_cc_code

        electronic_address = []
        for attach in attachments:
            file_name = attach.attachment_file.name
            file_extension = file_name.split(".")[-1].lower()

            if file_extension == 'pdf':
                file_type = 'PDF'
            else:
                file_type = 'TEXTO'

            view_url = "%sdocument/view/%s" % (settings.SITE_URL,  attach.short_url)

            electronic_address.append({'_u': view_url, '_i': attach.language[:2],
                                       '_y': file_type, '_q': file_extension})

        if electronic_address:
            if bundle.data['electronic_address'] and type(bundle.data['electronic_address']) is list:
                bundle.data['electronic_address'].extend(electronic_address)
            else:
                bundle.data['electronic_address'] = electronic_address

        if complement_data:
            # add fields of complement (event/project) to bundle
            complement = complement_data[0]
            for field in complement._meta.get_fields():
                if field.name != 'source' and field.name != 'id':
                    field_value = getattr(complement, field.name, {})
                    if field_value:
                        bundle.data[field.name] = copy(field_value)

        if library_records:
            for library in library_records:
                for field in library._meta.get_fields():
                    # ignore control fields
                    if field.name != 'source' and field.name != 'id' and field.name != 'cooperative_center_code':
                        field_value = getattr(library, field.name, {})
                        if field_value:
                            # convert lines of database field in list
                            if field.name == 'database' or field.name == 'local_descriptors':
                                field_value = [line.strip() for line in field_value.split('\n') if line.strip()]

                            # check if field already in bundle
                            if field.name in bundle.data:
                                # if field in bundle check is a list, otherwise convert to list
                                if type(bundle.data[field.name]) is not list:
                                    previous_value = bundle.data[field.name]
                                    bundle.data[field.name] = list(previous_value)
                            else:
                                bundle.data[field.name] = list()

                            # append field_value to bundle
                            if type(field_value) is list:
                                bundle.data[field.name].extend(field_value)
                            else:
                                bundle.data[field.name].append(field_value)

        # mark records that has status INPROCESS as LILACSEXPRESS #859
        if bundle.obj.status == 0:
            if 'database' in bundle.data:
                bundle.data['database'].append('LILACSEXPRESS')
            else:
                bundle.data['database'] = 'LILACSEXPRESS'


        return bundle

    def get_last_id(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        response = Reference.objects.latest('pk').pk

        return self.create_response(request, response)

    def dict2json(self, raw_dict):
        clean_dict = {k: v for k, v in raw_dict.items() if v}
        json_out = json.dumps(clean_dict, ensure_ascii=False).encode('utf8')

        return json_out
