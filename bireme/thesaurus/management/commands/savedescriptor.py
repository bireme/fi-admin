from django.core.management.base import BaseCommand, CommandError
from thesaurus.models_descriptors import *
from thesaurus.models_full import Descriptor

import time


class Command(BaseCommand):
	help = 'Migrate Descriptor full information to thesaurus_descriptor Model. By default migrates all Descriptors. ' \
		'Use --id to migrate specific Descriptor or --from --total to migrate a range of Descriptors'

	def add_arguments(self, parser):
		parser.add_argument('--id', nargs='+', type=int, help='The id of Descriptor to migrate')
		parser.add_argument('--total', type=int, help='Total of Descriptors to migrate')
		parser.add_argument('--from', type=int, default=1, help='Start id for migration (default = 1)')

	def handle(self, *args, **options):
		start = time.time()

		if options['id']:
			id_descriptors = IdentifierDesc.objects.using('decs_portal').filter(pk__in=options['id']).order_by('id')
		elif options['total'] and options['from']:
			id_descriptors = IdentifierDesc.objects.using('decs_portal').filter(
				pk__in=range(options['from'], options['from'] + options['total'])).order_by('id')
		elif options['total']:
			id_descriptors = IdentifierDesc.objects.using('decs_portal').filter(pk__in=range(1, 1 + options['total'])).order_by('id')
		elif options['from']:
			id_descriptors = IdentifierDesc.objects.using('decs_portal').filter(pk__gte=options['from']).order_by('id')
		else:
			id_descriptors = IdentifierDesc.objects.using('decs_portal').all().order_by('id')

		for id_descriptor in id_descriptors:
			identifier_id = id_descriptor.id
			if id_descriptor.descriptor_class == '1':
				descriptor_type = "TopicalDescriptor"
			elif id_descriptor.descriptor_class == '2':
				descriptor_type = "PublicationType"
			elif id_descriptor.descriptor_class == '3':
				descriptor_type = "CheckTag"
			elif id_descriptor.descriptor_class == '4':
				descriptor_type = "GeographicDescriptor"

			descriptions = id_descriptor.descriptiondesc.all()
			annotation_list = []
			history_note_list = []
			online_note_list = []
			public_note_list = []
			consider_also_list = []
			for description in descriptions:
				if description.annotation:
					annotation = {'@value': description.annotation, '@language': description.language_code}
					annotation_list.append(annotation)
				if description.history_note:
					history_note = {'@value': description.history_note, '@language': description.language_code}
					history_note_list.append(history_note)
				if description.online_note:
					online_note = {'@value': description.online_note, '@language': description.language_code}
					online_note_list.append(online_note)
				if description.public_mesh_note:
					public_note = {'@value': description.public_mesh_note, '@language': description.language_code}
					public_note_list.append(public_note)
				if description.consider_also:
					consider_also = {'@value': description.consider_also, '@language': description.language_code}
					consider_also_list.append(consider_also)

			if not annotation_list:
				annotation_list = None
			if not history_note_list:
				history_note_list = None
			if not online_note_list:
				online_note_list = None
			if not public_note_list:
				public_note_list = None
			if not consider_also_list:
				consider_also_list = None

			tree_numbers = id_descriptor.dtreenumbers.all()
			tree_number_list = []
			for tree_number in tree_numbers:
				tree_number_list.append(tree_number.tree_number)

			terms = TermListDesc.objects.using('decs_portal').filter(
				identifier_concept__identifier_id=identifier_id,
				).order_by('identifier_concept_id')
			label_list = []
			synonym_list = []
			concept_list = []
			active = 0
			for term in terms:
				term_json = {'@value': term.term_string, '@language': term.language_code, 'status': term.status}
				if term.record_preferred_term == 'Y':
					label_list.append(term_json)
					if term.language_code == 'en':
						# condicion de idioma para q lo haga una sola vez y tiene term_ui correcto
						active = 1
						preferred_term = term.term_ui
						preferred_concept = term.identifier_concept.concept_ui
						concept_descriptions = ConceptListDesc.objects.using('decs_portal').filter(identifier_concept=term.identifier_concept_id)
						scope_note_list = []
						for concept_description in concept_descriptions:
							if concept_description.scope_note:
								scope_note = {'@value': concept_description.scope_note, '@language': concept_description.language_code}
								scope_note_list.append(scope_note)
				else:
					if term_json not in synonym_list:
						synonym_list.append(term_json)
					if term.language_code == 'en' and term.identifier_concept.concept_ui not in concept_list:
						# condicion de idioma para q no agregue el preferred_concept
						concept_list.append(term.identifier_concept.concept_ui)

			if not synonym_list:
				synonym_list = None

			if not concept_list:
				concept_list = None

			pharmacological_list = []
			pharmacological_actions = list(id_descriptor.pharmacodesc.filter(
				descriptor_ui__isnull=False,
				term_string__isnull=False,
				language_code='en').order_by('descriptor_ui').values_list('descriptor_ui', flat=True))

			if pharmacological_actions:
				action_terms = TermListDesc.objects.using('decs_portal').filter(
							identifier_concept__identifier__descriptor_ui__in=pharmacological_actions,
							record_preferred_term='Y'
							).order_by('identifier_concept__identifier')
				action_ui = ''
				for action_term in action_terms:
					if action_term.identifier_concept.identifier.descriptor_ui != action_ui:
						if action_ui:
							pharmacological_list.append({'identifier': action_ui, 'label': action_label})
						action_label = []
						action_ui = action_term.identifier_concept.identifier.descriptor_ui
						action_label.append({'@value': action_term.term_string, '@language': action_term.language_code, 'status': action_term.status})
					else:
						action_label.append({'@value': action_term.term_string, '@language': action_term.language_code, 'status': action_term.status})
				if action_ui:
					# se agrega el ultimo procesado
					pharmacological_list.append({'identifier': action_ui, 'label': action_label})

			if not pharmacological_list:
				pharmacological_list = None

			related_list = []
			see_related = list(id_descriptor.relateddesc.filter(
				descriptor_ui__isnull=False,
				term_string__isnull=False).order_by('descriptor_ui').values_list('descriptor_ui', flat=True))
			if see_related:
				related_terms = TermListDesc.objects.using('decs_portal').filter(
							identifier_concept__identifier__descriptor_ui__in=see_related,
							record_preferred_term='Y',
							).order_by('identifier_concept__identifier_id')

				related_ui = ''
				for related_term in related_terms:
					if related_term.identifier_concept.identifier.descriptor_ui != related_ui:
						if related_ui:
							related_list.append({'identifier': related_ui, 'label': related_label})
						related_label = []
						related_ui = related_term.identifier_concept.identifier.descriptor_ui
						related_label.append({'@value': related_term.term_string, '@language': related_term.language_code, 'status': related_term.status})
					else:
						related_label.append({'@value': related_term.term_string, '@language': related_term.language_code, 'status': related_term.status})
				if related_ui:
					# se agrega el ultimo procesado
					related_list.append({'identifier': related_ui, 'label': related_label})

			if not related_list:
				related_list = None

			previous = id_descriptor.previousdesc.filter(previous_indexing__isnull=False)
			previous_list = []
			for previo in previous:
				previous_list.append({'@value': previo.previous_indexing, '@language': previo.language_code})

			if not previous_list:
				previous_list = None

			id_allowable_qualifiers = id_descriptor.abbreviation.all()
			allowed_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(id__in=id_allowable_qualifiers).order_by('abbreviation')
			qualifier_list = []
			for qualifier in allowed_qualifiers:
				qualifier_list.append({'identifier': qualifier.qualifier_ui, 'abbreviation': qualifier.abbreviation,
															'decs_code': str(qualifier.decs_code)})

			if not qualifier_list:
				qualifier_list = None

			entry_combination_list = []
			combination_list = id_descriptor.entrycombinationlistdesc.all()
			for combination in combination_list:
				qualifier_abbr = IdentifierQualif.objects.using('decs_portal').get(qualifier_ui=combination.ecin_id)
				ec_attr = {'sh_abbr1': qualifier_abbr.abbreviation}

				if combination.ecout_qualif_id:
					if combination.ecout_qualif_id != combination.ecin_id:
						qualifier_abbr1 = IdentifierQualif.objects.using('decs_portal').get(qualifier_ui=combination.ecout_qualif_id)
						ec_attr['sh_abbr2'] = qualifier_abbr1.abbreviation
					else:
						ec_attr['sh_abbr2'] = qualifier_abbr.abbreviation

				combination_terms = TermListDesc.objects.using('decs_portal').filter(
					identifier_concept__identifier__descriptor_ui=combination.ecout_desc_id,
					record_preferred_term='Y',
					term_string__isnull=False)

				combination_label = []
				for combination_term in combination_terms:
					combination_label.append({'@value': combination_term.term_string, '@language': combination_term.language_code,
						'status': combination_term.status})

				entry_combination_list.append({'label': combination_label, 'attr': ec_attr})

			if not entry_combination_list:
				entry_combination_list = None

			descriptor = Descriptor(
				id=identifier_id,
				thesaurus=id_descriptor.thesaurus.id,
				identifier=id_descriptor.descriptor_ui,
				decs_code=id_descriptor.decs_code,
				treeNumber=tree_number_list,
				nlmClassificationNumber=id_descriptor.nlm_class_number,
				date_created=id_descriptor.date_created,
				date_revised=id_descriptor.date_revised,
				date_established=id_descriptor.date_established,
				annotation=annotation_list,
				historyNote=history_note_list,
				onlineNote=online_note_list,
				publicMeSHNote=public_note_list,
				considerAlso=consider_also_list,
				preferredConcept=preferred_concept,
				concept=concept_list,
				scopeNote=scope_note_list,
				label=label_list,
				synonym=synonym_list,
				active=active,
				type=descriptor_type,
				preferredTerm=preferred_term,
				pharmacologicalAction=pharmacological_list,
				previousIndexing=previous_list,
				allowableQualifier=qualifier_list,
				seeAlso=related_list,
				entryCombination=entry_combination_list,
			)
			descriptor.save(using='decs_portal')
			self.stdout.write('Successfully saved "%s" Full Descriptor' % identifier_id)

		exec_time = time.time()-start
		self.stdout.write('Execution time "%s"' % time.strftime("%H:%M:%S",time.gmtime(exec_time)))
