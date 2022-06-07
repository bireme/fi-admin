from django.db.models.functions import Length, Substr
from django.core.management.base import BaseCommand, CommandError
from thesaurus.models_descriptors import *
from thesaurus.models_full import TreeDescriptor, TreeQualifier
from api.decs_first_level import *

import time


class Command(BaseCommand):
	help = 'Save full hierarchical information of Descriptors or Qualifiers to thesaurus_tree Model. ' \
	'Enter type of tree number to save: "D" for Descriptor or "Q" for Qualifier. By default saves all TreeNumbers. Use --tree_number to save specific TreeNumber or ' \
  '--from --total to save a range'

	def add_arguments(self, parser):
		parser.add_argument('type', help="Type of tree number to save 'D' for Descriptor or 'Q' for Qualifier")
		# parser.add_argument('--all', default=True, help='To save all Tree Numbers hierarchical information')
		parser.add_argument('--tree_number', help='The tree number of Descriptor to save the hierarchical information ')
		parser.add_argument('--total', type=int, help='Total of tree numbers to save')
		parser.add_argument('--from', type=int, default=1, help='Start id of tree numbers (default = 1)')

	def handle(self, *args, **options):
		start = time.time()

		if options['type'] == "D":
			TreeNumbersList = TreeNumbersListDesc
			TermList = TermListDesc
			IdentifierTable = IdentifierDesc
			FullTree = TreeDescriptor
			is_descriptor = True
			# opt_type = 'Descriptor'
		elif options['type'] == "Q":
			TreeNumbersList = TreeNumbersListQualif
			TermList = TermListQualif
			IdentifierTable = IdentifierQualif
			FullTree = TreeQualifier
			is_descriptor = False
			# opt_type = 'Qualifier'
		else:
			raise CommandError("Enter the correct type of tree number: 'D' for Descriptor or 'Q' for Qualifier")

		if options['tree_number']:
			try:
				tree_numbers = TreeNumbersList.objects.using('decs_portal').filter(tree_number=options['tree_number']).order_by('id')
			except TreeNumbersList.DoesNotExist:
				raise CommandError('Tree Number "%s" does not exist' % options['tree_number'])
		elif options['total'] and options['from']:
				tree_numbers = TreeNumbersList.objects.using('decs_portal').filter(
					pk__in=range(options['from'], options['from'] + options['total'])).order_by('id')
		elif options['total']:
			tree_numbers = TreeNumbersList.objects.using('decs_portal').filter(
				pk__in=range(1, 1 + options['total'])).order_by('id')
		elif options['from']:
			tree_numbers = TreeNumbersList.objects.using('decs_portal').filter(pk__gte=options['from']).order_by('id')
		else:
			tree_numbers = TreeNumbersList.objects.using('decs_portal').all().order_by('id')

		for tree_number in tree_numbers:
			tree_id = tree_number.tree_number
			identifier_obj = IdentifierTable.objects.using('decs_portal').get(pk=tree_number.identifier_id)
			ths = identifier_obj.thesaurus_id

			ancestor_term_list = []
			ancestors_tree_id = []

			parts = tree_id.split(".")
			# delete last
			parts.pop()

			# Ancestor only from first level categories  (ex: tree_number:A01 ancestor A)
			if not parts:
				category_id = get_category_id(tree_id)
				ancestors_tree_id.append(category_id)
			else:
				ancestor = ''
				for p in parts:
					if ancestor == '':
						ancestor = p
					else:
						ancestor = ancestor + '.' + p
					ancestors_tree_id.append(ancestor)

				# Obtener identifier _id para buscar term,
				# Hay q hacerlo en 2 pasos pq no se puede relacionar mas de 3 tablas
				ancestors_list = list(TreeNumbersList.objects.using('decs_portal').filter(
					tree_number__in=ancestors_tree_id,
					identifier__thesaurus=ths
				).order_by('tree_number').values('identifier_id', 'tree_number'))

			part1 = ""
			for tree_id_ancestor in ancestors_tree_id:
				if len(tree_id_ancestor) < 3:
					# llenar ancestor_label con category en todos los lang
					category_label = get_category_label(tree_id_ancestor, is_descriptor)
					ancestor_term_list.append({'label': category_label, 'attr': {'tree_id': tree_id_ancestor}})
				else:
					for ancestor_ids in ancestors_list:
						if ancestor_ids['tree_number'] == tree_id_ancestor:
							# add first level categories
							parts = ancestor_ids['tree_number'].split(".")
							if parts[0] != part1:
								part1 = parts[0]
								category_id = get_category_id(part1)
								category_label = get_category_label(category_id, is_descriptor)
								ancestor_term_list.append({'label': category_label, 'attr': {'tree_id': category_id}})

							ancestor_terms = TermList.objects.using('decs_portal').filter(
								identifier_concept__identifier=ancestor_ids['identifier_id'],
								record_preferred_term='Y',
								)

							ancestor_label = []
							for ancestor_term in ancestor_terms:
								term_text = ancestor_term.term_string
								if not is_descriptor:
									term_text = "/" + term_text
								ancestor_label.append(
									{'@value': term_text, '@language': ancestor_term.language_code, 'status': ancestor_term.status})

							term = {
								'label': ancestor_label,
								'attr': {'tree_id': ancestor_ids['tree_number']}}

							ancestor_term_list.append(term)
							break

			if not ancestor_term_list:
				ancestor_term_list = None

			preceding_sibling = []
			following_sibling = []

			tam = len(tree_id)
			if tam > 4:
				ancestor_tree_id = tree_id[0:tam - 4]
			else:
				ancestor_tree_id = get_category_id(tree_id)

			# En 2 pasos pq no se puede relacionar mas de 3 tablas
			sibling_list = list(TreeNumbersList.objects.using('decs_portal').annotate(tree_number_tam=Length('tree_number')).filter(
				tree_number__startswith=ancestor_tree_id,
				tree_number_tam=tam,
				identifier__thesaurus=ths,
				).order_by('tree_number').values(
				'identifier_id',
				'tree_number'))

			with_descendant = list(TreeNumbersList.objects.using('decs_portal').annotate(
				descendant=Substr('tree_number', 1, tam), tree_number_tam=Length('tree_number')).filter(
				tree_number__startswith=ancestor_tree_id,
				tree_number_tam__gt=tam,
				identifier__thesaurus=ths,
			).order_by('tree_number').values('descendant'))

			for sibling_ids in sibling_list:
				sibling_terms = TermList.objects.using('decs_portal').filter(
					identifier_concept__identifier=sibling_ids['identifier_id'],
					record_preferred_term='Y',
					)

				sibling_label = []
				for sibling_term in sibling_terms:
					term_text = sibling_term.term_string
					if not is_descriptor:
						term_text = "/" + term_text

					sibling_label.append(
						{'@value': term_text, '@language': sibling_term.language_code, 'status': sibling_term.status})

				term = {
					'label': sibling_label,
					'attr': {'tree_id': sibling_ids['tree_number']}}

				if {'descendant': sibling_ids['tree_number']} not in with_descendant:
					term['attr']['leaf'] = "true"

				if sibling_ids['tree_number'] < tree_id:
					preceding_sibling.append(term)
				elif sibling_ids['tree_number'] > tree_id:
					following_sibling.append(term)
				else:
					self_term = term

			if not preceding_sibling:
				preceding_sibling = None
			if not following_sibling:
				following_sibling = None

			descendant_term_list = []
			tree_number_starts = tree_id + '.'
			tam1 = tam + 4
			if 'leaf' not in self_term['attr'].keys():
				descendant_list = list(TreeNumbersList.objects.using('decs_portal').annotate(tree_number_tam=Length('tree_number')).filter(
					tree_number__startswith=tree_number_starts,
					tree_number_tam=tam1,
					identifier__thesaurus=ths,
				).order_by('tree_number').values('identifier_id', 'tree_number'))

				with_descendant = list(TreeNumbersList.objects.using('decs_portal').annotate(
					descendant=Substr('tree_number', 1, tam1), tree_number_tam=Length('tree_number')).filter(
					tree_number__startswith=tree_number_starts,
					tree_number_tam__gt=tam1,
					identifier__thesaurus=ths,
				).order_by('tree_number').values('descendant'))

				for descendant_ids in descendant_list:
					descendant_terms = TermList.objects.using('decs_portal').filter(
						identifier_concept__identifier=descendant_ids['identifier_id'],
						record_preferred_term='Y')

					descendant_label = []
					for descendant_term in descendant_terms:
						term_text = descendant_term.term_string
						if not is_descriptor:
							term_text = "/" + term_text

						descendant_label.append(
							{'@value': term_text, '@language': descendant_term.language_code, 'status': descendant_term.status})

					term = {
						'label': descendant_label,
						'attr': {'tree_id': descendant_ids['tree_number']}}

					if {'descendant': descendant_ids['tree_number']} not in with_descendant:
						term['attr']['leaf'] = "true"

					descendant_term_list.append(term)

			if not descendant_term_list:
				descendant_term_list = None

			tree = FullTree(
				id=tree_number.id,
				identifier_id=tree_number.identifier_id,
				treeNumber=tree_id,
				ancestor=ancestor_term_list,
				preceding_sibling=preceding_sibling,
				following_sibling=following_sibling,
				self_term=self_term,
				descendant=descendant_term_list
			)
			tree.save(using='decs_portal')
			self.stdout.write('Successfully saved "%s", identifier_id "%s", ths "%s" Full Hierarchical Info' % (tree_id, tree_number.identifier_id, ths))

		exec_time = time.time()-start
		self.stdout.write('Execution time "%s"' % time.strftime("%H:%M:%S", time.gmtime(exec_time)))


"""
# Get tree info from TreeDescriptor or TreeQualifier
			if tree_number[0:1] not in ["Q", "Y"]:
				TreeFull = TreeDescriptor
			else:
				TreeFull = TreeQualifier

ancestor_term_list = []
for tree_id in tree_ids:
	tree_obj = TreeFull.objects.using('decs_portal').get(identifier_id=identifier_id, treeNumber=tree_id['tree_id'])
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
		tree['self'] = {'term_list': {'term': label['@value'], 'attr': full_tree.self_term['attr']}, 'attr': {'lang': lang}}
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
"""
