# coding: utf-8
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.resources import ModelResource

from api.thesaurus_dtreenumber_api import ThesaurusResource

from thesaurus.models import *


class IdentifierQualifierResource(ModelResource):
	thesaurus = fields.ForeignKey(ThesaurusResource, 'thesaurus', full=True)

	class Meta:
		queryset = IdentifierQualif.objects.all()
		allowed_methods = ['get']
		resource_name = 'identifier_qualifier'
		excludes = ['created_time', 'date_created', 'date_established', 'date_revised', 'updated_time']
		filtering = {
			'id': ALL,
			'thesaurus': ALL_WITH_RELATIONS,
		}
		include_resource_uri = False


class QualifierTreeNumberResource(ModelResource):
	identifier = fields.ForeignKey(IdentifierQualifierResource, 'identifier', full=True)

	class Meta:
		queryset = TreeNumbersListQualif.objects.all()
		allowed_methods = ['get']
		resource_name = 'qtree_number'
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
		orm_filters = super(QualifierTreeNumberResource, self).build_filters(filters)
		# identifier__thesaurus =  1 <=> thesaurus = decs
		if 'ths' in filters:
			orm_filters['identifier__thesaurus'] = filters['ths']
		else:
			orm_filters['identifier__thesaurus'] = 1

		if 'tree_id' in filters:
			orm_filters['tree_number'] = filters['tree_id']

		return orm_filters

