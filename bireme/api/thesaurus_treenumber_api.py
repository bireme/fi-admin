from django.db.models.functions import Length, Substr
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404

from tastypie.resources import Resource, Bundle, BadRequest
# from tastypie.paginator import Paginator
from tastypie.utils.mime import determine_format

from haystack.query import SearchQuerySet

from api.thesaurus_dtreenumber_api import *
from api.thesaurus_qtreenumber_api import *
from api.decs_first_level import *
from api.thesaurus_dwords_api import DescriptorTermResource

# from itertools import chain

from api.ws_decs_serializer import WsDecsSerializer


class NoPaginator(Paginator):
	def page(self):
		output = super(NoPaginator, self).page()

		if output['meta']['total_count'] == 1 or output['meta']['total_count'] == 0:
			del output['meta']

		return output


class TreeNumberObject(object):
	def __init__(self, id=None, tree_number=None, identifier_concept=None):
		self.id = id
		self.tree_number = tree_number
		self.identifier_concept = identifier_concept


class TreeNumberResource(Resource):
	id = fields.IntegerField(attribute='id')
	tree_number = fields.CharField(attribute='tree_number', null=True, blank=True)
	identifier_concept = fields.CharField(attribute='identifier_concept', null=True, blank=True)

	class Meta:
		resource_name = 'tree_number'
		allowed_methods = ['get']
		object_class = TreeNumberObject
		include_resource_uri = False
		serializer = WsDecsSerializer(formats=['xml', 'json'])
		# elimina datos de paginacion
		paginator_class = NoPaginator

	def determine_format(self, request):
		"""
		return application/xml as the default format, request uri does not need format=xml
		"""
		fmt = determine_format(request, self._meta.serializer, default_format='application/xml')

		return fmt

	def get_object_list(self, bundle, **kwargs):
		if 'tree_id' in bundle.request.GET:
			tree_id = bundle.request.GET.get('tree_id', None)
			if not tree_id:
				# First Level Categories Case, array with one object to fill in dehydrate
				return [TreeNumberObject(1, "A")]
			elif tree_id[0:1] not in ["Q", "Y"]:
				# Descriptor Case
				descriptors = DescriptorTreeNumberResource().obj_get_list(bundle, **kwargs)
				return descriptors
			else:
				# Qualifier Case
				qualifiers = QualifierTreeNumberResource().obj_get_list(bundle, **kwargs)
				return qualifiers
		elif 'words' in bundle.request.GET:
			# terms = DescriptorTermResource().get_search(bundle.request, **kwargs)
			# return terms
			self.method_check(bundle.request, allowed=['get'])
			self.is_authenticated(bundle.request)
			self.throttle_check(bundle.request)

			# Do the query.
			sqs = SearchQuerySet().models(TermListDesc).load_all().auto_query(bundle.request.GET.get('words', ''))
			# return sqs
			paginator = Paginator(sqs, 20)
			page = paginator.page(int(bundle.request.GET.get('page', 1)))
			results = []
			for result in page.object_list:
				new_obj = TreeNumberObject(result.id, "", result.identifier_concept)
				results.append(new_obj)

			return results

			# result.object['tree_number'] = "A01"  # error: no se permite asignar items
			# return page.object_get_list

		else:
			raise BadRequest("Missing tree_id parameter")
		# Sort the merged list alphabetically and just return the top 20
		# return sorted(chain(objects_one, objects_two), key=lambda instance: instance.identifier())[:20]

	def obj_get_list(self, bundle, **kwargs):
		return self.get_object_list(bundle, **kwargs)

	def dehydrate(self, bundle):
		# default thesaurus 1 (decs)
		ths = bundle.request.GET.get('ths', 1)

		# default language pt
		lang = bundle.request.GET.get('lang', 'pt')

		if lang == 'pt':
			# language_code in DB is pt-br not pt
			lang_code = 'pt-br'
		else:
			lang_code = lang

		by_tree_id = bundle.request.GET.get('tree_id', None)
		if by_tree_id:
			if bundle.obj.tree_number == "A":
				# first level categories
				decsws_response = {
					'attr': {
						'service': "",
						'tree_id': "",
					},
					'tree': {'term_list': first_level_list(lang_code), 'attr': {'lang': lang}}
				}
			else:
				if bundle.obj.tree_number[0:1] not in ["Q", "Y"]:
					is_descriptor = True
					# descriptor models
					TermList = TermListDesc
					TreeNumbersList = TreeNumbersListDesc
					ConceptList = ConceptListDesc
					Description = DescriptionDesc
				else:
					is_descriptor = False
					# qualifier models
					TermList = TermListQualif
					TreeNumbersList = TreeNumbersListQualif
					ConceptList = ConceptListQualif
					Description = DescriptionQualif

				decsws_response = {
					'attr': {
						'service': "",
						'tree_id': bundle.obj.tree_number,
					}
				}
				identifier_id = bundle.obj.identifier.id

				record_list = {}
				record = {
					"attr": {
						"lang": lang,
						"db": 'decs',
						"mfn": bundle.obj.identifier.decs_code,
					}
				}
				if is_descriptor:
					record["unique_identifier_nlm"] = bundle.obj.identifier.descriptor_ui
				else:
					record["unique_identifier_nlm"] = bundle.obj.identifier.qualifier_ui

				term_attr_list = []
				term_string = None
				term_list = list(TermList.objects.filter(
					identifier_concept__identifier_id=identifier_id,
					identifier_concept__preferred_concept='Y',
					concept_preferred_term='Y',
					status=1).values('term_string', 'language_code'))
				for term in term_list:
					if term['language_code'] == 'pt-br' and lang == 'pt':
						show_lang = 'pt'
					else:
						show_lang = term['language_code']

					if not is_descriptor:
						term['term_string'] = "/" + term['term_string']
					term_attr = {
						'attr': {'lang': show_lang}, 'descriptor': term['term_string'],
					}
					term_attr_list.append(term_attr)

					if term['language_code'] == lang_code:
						# to use in <tree><self><term_list><term>
						term_string = term['term_string']

					if term['language_code'] == 'en':
						term_string_en = term['term_string']

				record['descriptor_list'] = term_attr_list

				synonym_list = list(TermList.objects.filter(
					identifier_concept__identifier_id=identifier_id,
					identifier_concept__preferred_concept='N',
					concept_preferred_term='N',
					language_code=lang_code,
					status=1).values('term_string'))
				for synonym in synonym_list:
					if not is_descriptor:
						synonym['term_string'] = "/" + synonym['term_string']
					synonym['synonym'] = synonym.pop('term_string')
				record['synonym_list'] = synonym_list

				tree_ids = []
				tree_id_list = list(TreeNumbersList.objects.filter(
					identifier_id=identifier_id).values('tree_number'))
				for tree_id in tree_id_list:
					if is_descriptor or (not is_descriptor and tree_id['tree_number'][0:1] == bundle.obj.tree_number[0:1]):
						tree_ids.append({'tree_id': tree_id['tree_number']})
				record["tree_id_list"] = tree_ids

				# definition = ConceptListDesc.scope_note
				definition = ConceptList.objects.filter(
					identifier_concept__identifier_id=identifier_id,
					identifier_concept__preferred_concept='Y',
					language_code=lang_code).values('scope_note').first()
				if definition:
					record['definition'] = {"occ": {"attr": {"n": definition['scope_note']}} }

				annotation = Description.objects.filter(
					identifier_id=identifier_id,
					language_code=lang_code).values().first()
				if annotation and annotation['annotation']:
					record['indexing_annotation'] = annotation['annotation']

				if is_descriptor:
					if annotation and annotation['consider_also']:
						record['consider_also_terms_at'] = annotation['consider_also']

					pharmacological_action = list(PharmacologicalActionList.objects.filter(
						identifier_id=identifier_id,
						descriptor_ui__isnull=False,
						language_code='en').order_by('descriptor_ui').values_list('descriptor_ui', flat=True))

					pharmacological_action_list = []
					if pharmacological_action:
						action_terms = TermList.objects.filter(
							identifier_concept__identifier__descriptor_ui__in=pharmacological_action,
							record_preferred_term='Y',
							language_code=lang_code,
							status=1).order_by('identifier_concept__identifier')
						for action_term in action_terms:
							pharmacological_action_list.append({'pharmacological_action': action_term.term_string, 'attr':{'lang': lang}})
					record['pharmacological_action_list'] = pharmacological_action_list

					entry_combination_list = []
					combination_list = list(EntryCombinationListDesc.objects.filter(
						identifier_id=identifier_id).values('ecin_id', 'ecout_desc_id', 'ecout_qualif_id'))
					for combination in combination_list:
						ec_attr = {'lang': lang}
						qualifier_abbr = IdentifierQualif.objects.get(qualifier_ui=combination['ecin_id'])
						ec_attr['sh_abbr1'] = qualifier_abbr.abbreviation

						if combination['ecout_qualif_id']:
							if combination['ecout_qualif_id'] != combination['ecin_id']:
								qualifier_abbr1 = IdentifierQualif.objects.get(qualifier_ui=combination['ecout_qualif_id'])
								ec_attr['sh_abbr2'] = qualifier_abbr1.abbreviation
							else:
								ec_attr['sh_abbr2'] = qualifier_abbr.abbreviation

						combination_term = TermList.objects.filter(
							identifier_concept__identifier__descriptor_ui=combination['ecout_desc_id'],
							identifier_concept__preferred_concept='Y',
							concept_preferred_term='Y',
							record_preferred_term='Y',
							language_code=lang_code,
							status=1)

						if combination_term:
							term_text = combination_term[0].term_string
						else:
							term_text = ""

						entry_combination_list.append({'entry_combination': term_text, 'attr': ec_attr})

					record['entry_combination_list'] = entry_combination_list

					see_related_list = []
					related_list = list(SeeRelatedListDesc.objects.filter(
						identifier_id=identifier_id).values('descriptor_ui'))
					for related in related_list:
						related_term = TermList.objects.filter(
							identifier_concept__identifier__descriptor_ui=related['descriptor_ui'],
							identifier_concept__preferred_concept='Y',
							concept_preferred_term='Y',
							record_preferred_term='Y',
							language_code=lang_code,
							status=1)

						if related_term:
							term_text = related_term[0].term_string.encode('utf-8')
						else:
							# does not exists translation
							term_text = ""

						see_related_list.append({'see_related': term_text, 'attr': {'lang': lang}})

					record['see_related_list'] = see_related_list

					allowable_qualifier_list = list(bundle.obj.identifier.abbreviation.values(
						'abbreviation', 'decs_code').order_by('abbreviation'))

					for abbr in allowable_qualifier_list:
						abbr['allowable_qualifier'] = abbr.pop('abbreviation')
						abbr['attr'] = {'id': str(abbr['decs_code'])}
						abbr.pop('decs_code')
					record['allowable_qualifier_list'] = allowable_qualifier_list
				else:
					record['pharmacological_action_list'] = []
					record['entry_combination_list'] = []
					record['see_related_list'] = []
					record['allowable_qualifier_list'] = []

				record_list['record'] = record

				decsws_response['record_list'] = record_list

				tree = {}

				tree_id_ancestor_list = []
				ancestor_term_list = []
				ancestors_tree_id = []
				for tree_id in tree_ids:
					parts = tree_id['tree_id'].split(".")
					# delete last
					parts.pop()

					# Ancestor only from first level categories  (ex: tree_id:A01 ancestor A)
					if not parts:
						category_id = get_category_id(tree_id['tree_id'])
						tree_id_ancestor_list.append({'tree_id': tree_id, 'ancestor': category_id})

					ancestor = ''
					for p in parts:
						if ancestor == '':
							ancestor = p
						else:
							ancestor = ancestor + '.' + p
						ancestors_tree_id.append(ancestor)
						tree_id_ancestor_list.append({'tree_id': tree_id, 'ancestor': ancestor})

				# Hay q hacerlo en 2 pasos pq no se puede relacionar mas de 3 tablas
				ancestors_list = list(TreeNumbersList.objects.filter(
					tree_number__in=ancestors_tree_id,
					identifier__thesaurus=ths,
					).order_by('tree_number').values('identifier_id', 'tree_number'))

				part1 = ""
				for tree_id_ancestor in tree_id_ancestor_list:
					if len(tree_id_ancestor['ancestor']) < 3:
						category = get_category(tree_id_ancestor['ancestor'], is_descriptor, lang)
						ancestor_term_list.append({'term': category, 'attr': {'tree_id': tree_id_ancestor['ancestor']}})
					else:
						for ancestor_ids in ancestors_list:
							if ancestor_ids['tree_number'] == tree_id_ancestor['ancestor']:
								# add first level categories
								parts = ancestor_ids['tree_number'].split(".")
								if parts[0] != part1:
									part1 = parts[0]
									category_id = get_category_id(part1)
									category = get_category(category_id, is_descriptor, lang)
									ancestor_term_list.append({'term': category, 'attr': {'tree_id': category_id}})

								ancestor_term = TermList.objects.filter(
									identifier_concept__identifier=ancestor_ids['identifier_id'],
									identifier_concept__preferred_concept='Y',
									concept_preferred_term='Y',
									record_preferred_term='Y',
									language_code=lang_code,
									status=1)

								if ancestor_term:
									term_text = ancestor_term[0].term_string
									if not is_descriptor:
										term_text = "/" + term_text
								else:
									# does notexist translation
									term_text = ""

								term = {
									'term': term_text,
									'attr': {'tree_id': ancestor_ids['tree_number']}}

								ancestor_term_list.append(term)
								break

				tree['ancestors'] = {'term_list': ancestor_term_list, 'attr': {'lang': lang}}

				preceding_sibling = []
				following_sibling = []

				tam = len(bundle.obj.tree_number)
				if tam > 4:
					ancestor_tree_id = bundle.obj.tree_number[0:tam-4]
				else:
					ancestor_tree_id = get_category_id(bundle.obj.tree_number)

				# En 2 pasos pq no se puede relacionar mas de 3 tablas
				sibling_list = list(TreeNumbersList.objects.annotate(tree_number_tam=Length('tree_number')).filter(
					tree_number__startswith=ancestor_tree_id,
					tree_number_tam=tam,
					identifier__thesaurus=ths,
					).exclude(tree_number__exact=bundle.obj.tree_number).order_by('tree_number').values('identifier_id', 'tree_number'))

				with_descendant = list(TreeNumbersList.objects.annotate(
					descendant=Substr('tree_number', 1, tam), tree_number_tam=Length('tree_number')).filter(
					tree_number__startswith=ancestor_tree_id,
					tree_number_tam__gt=tam,
					identifier__thesaurus=ths,
					).order_by('tree_number').values('descendant'))

				for sibling_ids in sibling_list:
					sibling_term = TermList.objects.filter(
						identifier_concept__identifier=sibling_ids['identifier_id'],
						identifier_concept__preferred_concept='Y',
						concept_preferred_term='Y',
						record_preferred_term='Y',
						language_code=lang_code,
						status=1)

					if sibling_term:
						term_text = sibling_term[0].term_string
						if not is_descriptor:
							term_text = "/" + term_text
					else:
						# does notexist translation
						term_text = ""

					term = {
						'term': term_text,
						'attr': {'tree_id': sibling_ids['tree_number']}}

					if {'descendant': sibling_ids['tree_number']} not in with_descendant:
						term['attr']['leaf'] = "true"

					if sibling_ids['tree_number'] < bundle.obj.tree_number:
						preceding_sibling.append(term)
					else:
						following_sibling.append(term)

				tree['preceding_sibling'] = {'term_list': preceding_sibling, 'attr': {'lang': lang}}
				tree['following_sibling'] = {'term_list': following_sibling, 'attr': {'lang': lang}}

				if not term_string:
					term_string = term_string_en

				if {'descendant': bundle.obj.tree_number} not in with_descendant:
					attr_self = {'tree_id': bundle.obj.tree_number, 'leaf': 'true'}
					leaf = 1
				else:
					attr_self = {'tree_id': bundle.obj.tree_number}
					leaf = 0

				self_descriptor = {
					'attr': {'lang': lang},
					'term_list': [
						{
							'term': term_string,
							'attr': attr_self
						},
					],
				}

				tree['self'] = self_descriptor

				descendant_term_list = []
				tree_number_starts = bundle.obj.tree_number + '.'
				tam1 = tam+4
				if not leaf:
					descendant_list = list(TreeNumbersList.objects.annotate(tree_number_tam=Length('tree_number')).filter(
						tree_number__startswith=tree_number_starts,
						tree_number_tam=tam1,
						identifier__thesaurus=ths,
						).order_by('tree_number').values('identifier_id', 'tree_number'))

					with_descendant = list(TreeNumbersList.objects.annotate(
						descendant=Substr('tree_number', 1, tam1), tree_number_tam=Length('tree_number')).filter(
						tree_number__startswith=tree_number_starts,
						tree_number_tam__gt=tam1,
						identifier__thesaurus=ths,
						).order_by('tree_number').values('descendant'))

					for descendant_ids in descendant_list:
						descendant_term = TermList.objects.filter(
							identifier_concept__identifier=descendant_ids['identifier_id'],
							identifier_concept__preferred_concept='Y',
							concept_preferred_term='Y',
							record_preferred_term='Y',
							language_code=lang_code,
							status=1)
						if descendant_term:
							term_text = descendant_term[0].term_string
							if not is_descriptor:
								term_text = "/" + term_text
						else:
							# does notexist translation
							term_text = ""

						term = {
							'term': term_text,
							'attr': {'tree_id': descendant_ids['tree_number']}}

						if {'descendant': descendant_ids['tree_number']} not in with_descendant:
							term['attr']['leaf'] = "true"

						descendant_term_list.append(term)

				tree['descendants'] = {'term_list': descendant_term_list, 'attr': {'lang': lang}}

				decsws_response['tree'] = tree

			bundle.data['decsws_response'] = decsws_response
		else:
			bundle.data['by_words'] = 'yes'

		# bundle.data.pop('identifier_descriptor')
		# bundle.data.pop('identifier_qualifier')
		# bundle.data.pop('tree_number')
		bundle.data.pop('id')

		return bundle


def get_category_id(tree_number):
	category_id = tree_number[0:1]
	if category_id not in ['Q', 'Y']:
		category_id2 = tree_number[1:2]
		if not category_id2.isdigit():
			category_id = category_id + category_id2

	return category_id


def get_category(category_id, is_descriptor, lang):
	if is_descriptor:
		category = category_translated(first_level_categories[category_id], lang)
	else:
		category = category_translated(_("Other Qualifiers"), lang)

	return category


"""
elif 'words' in bundle.request.GET:
	terms = DescriptorTermResource.get_search(bundle.request, **kwargs)
	return terms
"""
