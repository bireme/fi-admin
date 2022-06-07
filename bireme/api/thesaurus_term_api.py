from django.db.models.functions import Length, Substr
from django.conf import settings

from tastypie.resources import Resource
from tastypie.paginator import Paginator
from tastypie.utils.mime import determine_format
from tastypie import fields

# Modelos de thesaurus utilizados en las diferentes opciiones del ws decs
from thesaurus.models import TermListDesc, TreeNumbersListDesc, TermListQualif, TreeNumbersListQualif
# Modelos de tablas auxiliares de registro completo de descriptor y calificador
from thesaurus.models_full import *

# funciones para la busqueda en ElasticSearch y para parsear expresion bool
from api.esearch_functions import *
# Arreglo con categorias de 1er nivel y funciones de traduccion
from api.decs_first_level import *
# Serializador para que formato xml sea igual al del WS DeCS actual
from api.ws_decs_serializer import WsDecsSerializer

valid_lang = TermListDesc.objects.using("decs_portal").distinct().values("language_code")
DECS_LANGUAGES = [list(dict_lang.values())[0] for dict_lang in valid_lang]

# limitar traceback en las respuestas con error
# import sys
# sys.tracebacklimit=0

class NoPaginator(Paginator):

	def __init__(self, request_data, objects, resource_uri=None, limit=None, offset=0, max_limit=1000,
	             collection_name='objects'):
		# limit = 1000, Show all results
		super(NoPaginator, self).__init__(request_data, objects, resource_uri, 1000, offset, max_limit, collection_name)

	def page(self):
		output = super(NoPaginator, self).page()

		# no mostrar datos de meta (total de registros, ctdad en una pag, ...)
		del output['meta']

		return output


class TermObject(object):
	def __init__(self, identifier=None, term_type=None):
		self.identifier = identifier
		self.term_type = term_type


class TermResource(Resource):
	identifier = fields.IntegerField(attribute='identifier')
	term_type = fields.CharField(attribute='term_type', null=True, blank=True)

	class Meta:
		resource_name = 'term'
		allowed_methods = ['get']
		object_class = TermObject
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
		results = []
		terms = self.get_search(bundle.request, **kwargs)

		for term in terms:
			new_obj = TermObject(term['identifier'], term['term_type'])
			results.append(new_obj)

		return results

	def obj_get_list(self, bundle, **kwargs):
		return self.get_object_list(bundle, **kwargs)

	def get_search(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		self.is_authenticated(request)
		self.throttle_check(request)

		# default thesaurus 1 (decs)
		ths = request.GET.get('ths', '1')

		# default status 1 (decs)
		status = request.GET.get('status', '1')

		# default language pt
		lang = request.GET.get('lang', 'pt')

		valid_lang = get_valid_lang(lang)
		lang = valid_lang[0]
		lang_code = valid_lang[1]

		response = []
		if 'words' in request.GET:
			words = request.GET.get('words', '')
			search_words = get_search_q('words', words, None, status, lang_code, ths)
			response = execute_simple_search(search_words)

		elif 'bool' in request.GET:
			bool_query = request.GET.get('bool', '')

			query_parts = f_parse(bool_query)
			#if query_parts:
			response = complex_search(query_parts, status, lang_code, ths)
		elif 'tree_id' in request.GET:
			tree_id = request.GET.get('tree_id', None)
			if not tree_id:
				# First Level Categories Case, array with one object to fill in dehydrate
				response = [{'identifier': 1, 'term_type': "first_level"}]
			else:
				search_treeid = get_search_q('tree_id', tree_id, None, status, lang_code, ths)
				response = execute_simple_search(search_treeid)

		self.log_throttled_access(request)
		# para probar search desde la url
		# return self.create_response(request, object_list)

		return response

	def dehydrate(self, bundle):
		# default thesaurus 1 (decs)
		ths = bundle.request.GET.get('ths', 1)

		# default language pt
		lang = bundle.request.GET.get('lang', 'pt')

		valid_lang = get_valid_lang(lang)
		lang = valid_lang[0]
		lang_code = valid_lang[1]

		r_query = None
		if 'tree_id' in bundle.request.GET and bundle.obj.term_type=='first_level':
			# first level categories
			decsws_response = {
				'attr': {
					'service': "",
					'tree_id': "",
				},
				'tree': {'term_list': first_level_list(lang_code), 'attr': {'lang': lang}}
			}
		else:
			if bundle.obj.term_type == 'descriptor':
				is_descriptor = True
				# descriptor models
				TermFull = Descriptor
				TreeFull = TreeDescriptor
				TreeNumbersList = TreeNumbersListDesc
			else:
				is_descriptor = False
				# qualifier models
				TermFull = Qualifier
				TreeFull = TreeQualifier
				TreeNumbersList = TreeNumbersListQualif

			full_term = TermFull.objects.using('decs_portal').get(pk=bundle.obj.identifier)

			if 'tree_id' in bundle.request.GET:
				tree_number = bundle.request.GET.get('tree_id')
			else:
				# If term has many tree_number, we get first tree_number
				tree_number = full_term.treeNumber[0]
				if 'words' in bundle.request.GET:
					r_query = bundle.request.GET.get('words', '')
				elif 'bool' in bundle.request.GET:
					r_query = bundle.request.GET.get('bool', '')

			decsws_response = {
				'attr': {
					'service': "",
					'tree_id': tree_number,
				}
			}
			record_list = {}
			record = {
				"attr": {
					"lang": lang,
					"db": 'decs',
					"mfn": full_term.decs_code,
				},
				"unique_identifier_nlm": full_term.identifier
			}

			term_attr_list = []
			for term in full_term.label:
				if term['status'] == 1:
					if not is_descriptor:
						term['@value'] = "/" + term['@value']

					term_attr = {
						'attr': {'lang': term['@language']}, 'descriptor': term['@value'],
					}
					term_attr_list.append(term_attr)
					if term['@language'] == lang_code:
						# to use in <tree><self><term_list><term>
						term_string = term['@value']
					if term['@language'] == 'en':
						term_string_en = term['@value']

			record['descriptor_list'] = term_attr_list

			synonym_list = []
			if full_term.synonym:
				for term in full_term.synonym:
					if term['status'] == 1:
						if not is_descriptor:
							term['@value'] = "/" + term['@value']
						if term['@language'] == lang_code:
							synonym = {'synonym': term['@value']}
							synonym_list.append(synonym)

			record['synonym_list'] = synonym_list

			for scope_note in full_term.scopeNote:
				if scope_note['@language'] == lang_code:
					record['definition'] = {"occ": {"attr": {"n": scope_note['@value']}}}
					break

			tree_ids = []
			for tree_id in full_term.treeNumber:
				if (not is_descriptor and tree_number[0] == tree_id[0]) or is_descriptor:
					# si tree_number de qualifier con Q tree_ids con Q, si tree_number con Y tree_ids con Y
					tree_ids.append({'tree_id': tree_id})

			record["tree_id_list"] = tree_ids

			if full_term.annotation:
				for annotation in full_term.annotation:
					if annotation['@language'] == lang_code:
						record['indexing_annotation'] = annotation['@value']
						break

			if is_descriptor:
				if full_term.considerAlso:
					for consider_also in full_term.considerAlso:
						if consider_also['@language'] == lang_code:
							record['consider_also_terms_at'] = consider_also['@value']
							break

				pharmacological_list = []
				if full_term.pharmacologicalAction:
					for action in full_term.pharmacologicalAction:
						for label in action['label']:
							if label['status'] == 1 and label['@language'] == lang_code:
								pharmacological_list.append({'pharmacological_action': label['@value'], 'attr': {'lang': lang}})

				record['pharmacological_action_list'] = pharmacological_list

				entry_combination_list = []
				if full_term.entryCombination:
					for combination in full_term.entryCombination:
						for label in combination['label']:
							if label['status'] == 1 and label['@language'] == lang_code:
								ec_attr = combination['attr']
								ec_attr['lang'] = lang_code
								entry_combination_list.append({'entry_combination': label['@value'], 'attr': ec_attr})
						# break

				record['entry_combination_list'] = entry_combination_list

				see_related_list = []
				if full_term.seeAlso:
					for see_also in full_term.seeAlso:
						for label in see_also['label']:
							if label['status'] == 1 and label['@language'] == lang_code:
								see_related_list.append({'see_related': label['@value'], 'attr': {'lang': lang}})

				record['see_related_list'] = see_related_list

				allowable_qualifier_list = []
				if full_term.allowableQualifier:
					for allowable_qualifier in full_term.allowableQualifier:
						allowable_qualifier_list.append({'allowable_qualifier': allowable_qualifier['abbreviation'],
							'attr': {'id': str(allowable_qualifier['decs_code'])}})

				record['allowable_qualifier_list'] = allowable_qualifier_list

			else:
				record['pharmacological_action_list'] = []
				record['entry_combination_list'] = []
				record['see_related_list'] = []
				record['allowable_qualifier_list'] = []


			record_list['record'] = record
			decsws_response['record_list'] = record_list

			tree = {}

			# Get tree info form TreeDescriptor or TreeQualifier (mesh data model)
			ancestor_term_list = []
			for tree_id in tree_ids:
				# se busca 1ro id del tree_number pq es mucho mas lento buscar en TreeFull por (tree_number, identifier_id)
				tree_number_id = TreeNumbersList.objects.using('decs_portal').get(tree_number=tree_id['tree_id'], identifier_id=bundle.obj.identifier)
				tree_obj = TreeFull.objects.using('decs_portal').get(id=tree_number_id.id)
				if tree_id['tree_id'] == tree_number:
					# Self, sibling and descendant only for this tree_number
					full_tree = tree_obj
				for ancestor in tree_obj.ancestor:
					for label in ancestor['label']:
						if label['status'] == 1 and label['@language'] == lang_code:
							ancestor_term_list.append({'term': label['@value'], 'attr': ancestor['attr']})
							break
			tree['ancestors'] = {'term_list': ancestor_term_list, 'attr': {'lang': lang}}

			for label in full_tree.self_term['label']:
				if label['status'] == 1 and label['@language'] == lang_code:
					tree['self'] = {'term_list': {'term': label['@value'], 'attr': full_tree.self_term['attr']},
					                'attr': {'lang': lang}}
					break

			preceding_sibling = []
			if full_tree.preceding_sibling:
				for preceding in full_tree.preceding_sibling:
					for label in preceding['label']:
						if label['status'] == 1 and label['@language'] == lang_code:
							preceding_sibling.append({'term': label['@value'], 'attr': preceding['attr']})

			tree['preceding_sibling'] = {'term_list': preceding_sibling, 'attr': {'lang': lang}}

			following_sibling = []
			if full_tree.following_sibling:
				for following in full_tree.following_sibling:
					for label in following['label']:
						if label['status'] == 1 and label['@language'] == lang_code:
							following_sibling.append({'term': label['@value'], 'attr': following['attr']})

			tree['following_sibling'] = {'term_list': following_sibling, 'attr': {'lang': lang}}

			descendants = []
			if full_tree.descendant:
				for one_descendant in full_tree.descendant:
					for label in one_descendant['label']:
						if label['status'] == 1 and label['@language'] == lang_code:
							descendants.append({'term': label['@value'], 'attr': one_descendant['attr']})

			tree['descendants'] = {'term_list': descendants, 'attr': {'lang': lang}}

			decsws_response['tree'] = tree

		bundle.data.pop('identifier')
		bundle.data.pop('term_type')
		bundle.data['decsws_response'] = decsws_response
		if r_query:
			bundle.data['query'] = r_query

		return bundle


def get_valid_lang(lang):
	# valid_lang = [k[0:2] for k, v in settings.LANGUAGES]
	if lang[0:2] not in DECS_LANGUAGES:
		lang = 'pt'
		lang_code = 'pt-br'
	else:
		lang = lang[0:2]
		if lang == 'pt':
			lang_code = 'pt-br'
		else:
			lang_code = lang[0:2]

	return [lang, lang_code]