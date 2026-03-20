# coding: utf-8
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.resources import ModelResource

from thesaurus.models import *


class ThesaurusResource(ModelResource):
	class Meta:
		queryset = Thesaurus.objects.all()
		allowed_methods = ['get']
		resource_name = 'thesaurus'
		fields = ['id']
		include_resource_uri = False
		filtering = {
			"id": ('exact',)
		}


class QualifierAbbreviationResource(ModelResource):
	class Meta:
		queryset = IdentifierQualif.objects.all()
		allowed_methods = ['get']
		resource_name = 'qualifier_abbreviation'
		fields = ['abbreviation', 'decs_code']
		include_resource_uri = False


class IdentifierDescriptorResource(ModelResource):
	abbreviation = fields.ManyToManyField(QualifierAbbreviationResource, 'abbreviation', full=True)
	thesaurus = fields.ForeignKey(ThesaurusResource, 'thesaurus', full=True)

	class Meta:
		queryset = IdentifierDesc.objects.all()
		allowed_methods = ['get']
		resource_name = 'identifier_descriptor'
		excludes = ['created_time', 'updated_time', 'date_created', 'date_established', 'date_revised']
		filtering = {
			'id': ALL,
			'abbreviation': ALL_WITH_RELATIONS,
			'thesaurus': ALL_WITH_RELATIONS,
		}
		include_resource_uri = False


class DescriptorTreeNumberResource(ModelResource):
	identifier = fields.ForeignKey(IdentifierDescriptorResource, 'identifier', full=True)

	class Meta:
		queryset = TreeNumbersListDesc.objects.all()
		allowed_methods = ['get']
		resource_name = 'dtree_number'
		filtering = {
			'tree_id': ALL,
			'identifier': ALL_WITH_RELATIONS,
			'ths': ALL,
		}
		include_resource_uri = False

	def build_filters(self, filters=None):
		"""
		filter by thesaurus = 1 (decs) by default, or by filters['ths'] if is set
		filter by tree_number if filters['tree_id'] is set
		"""
		orm_filters = super(DescriptorTreeNumberResource, self).build_filters(filters)
		# identifier__thesaurus =  1 <=> thesaurus = decs
		if 'ths' in filters:
			orm_filters['identifier__thesaurus'] = filters['ths']
		else:
			orm_filters['identifier__thesaurus'] = 1

		if 'tree_id' in filters:
			orm_filters['tree_number'] = filters['tree_id']

		return orm_filters

