from django.core.management.base import BaseCommand, CommandError
from thesaurus.models_qualifiers import *
from thesaurus.models_full import Qualifier

import time


class Command(BaseCommand):
	help = "Migrate Qualifier's full information to thesaurus_qualifier Model. By default migrates all Qualifiers. " \
		"Use --id to migrate specific Qualifire or --from --total to migrate a range of Qualifiers"

	def add_arguments(self, parser):
		parser.add_argument('--id', nargs='+',type=int, help='The id of Qualifier to migrate')
		parser.add_argument('--total', type=int, help='Total of Qualifiers to migrate')
		parser.add_argument('--from', type=int, default=1, help='Start id for migration (default = 1)')

	def handle(self, *args, **options):
		start = time.time()

		if options['id']:
			id_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(pk__in=options['id']).order_by('id')
		elif options['total'] and options['from']:
			id_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(pk__in=range(options['from'], options['from']+options['total'])).order_by('id')
		elif options['total']:
			id_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(pk__in=range(1, 1 + options['total'])).order_by('id')
		elif options['from']:
			id_qualifiers = IdentifierQualif.objects.using('decs_portal').filter(pk__gte=options['from']).order_by('id')
		else:
			id_qualifiers = IdentifierQualif.objects.using('decs_portal').all().order_by('id')

		for id_qualifier in id_qualifiers:
			identifier_id = id_qualifier.id

			descriptions = id_qualifier.descriptionqualif.all()
			annotation_list = []
			history_note_list = []
			online_note_list = []
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

			if not annotation_list:
				annotation_list = None
			if not history_note_list:
				history_note_list = None
			if not online_note_list:
				online_note_list = None

			tree_numbers = id_qualifier.qtreenumbers.all()
			tree_number_list = []
			for tree_number in tree_numbers:
				tree_number_list.append(tree_number.tree_number)

			terms = TermListQualif.objects.using('decs_portal').filter(identifier_concept__identifier_id=identifier_id).order_by('identifier_concept_id')
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
						concept_descriptions = ConceptListQualif.objects.using('decs_portal').filter(identifier_concept=term.identifier_concept_id)
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

			descriptor = Qualifier(
				id=identifier_id,
				thesaurus=id_qualifier.thesaurus.id,
				identifier=id_qualifier.qualifier_ui,
				abbreviation=id_qualifier.abbreviation,
				decs_code=id_qualifier.decs_code,
				treeNumber=tree_number_list,
				date_created=id_qualifier.date_created,
				date_revised=id_qualifier.date_revised,
				date_established=id_qualifier.date_established,
				annotation=annotation_list,
				historyNote=history_note_list,
				onlineNote=online_note_list,
				preferredConcept=preferred_concept,
				concept=concept_list,
				scopeNote=scope_note_list,
				label=label_list,
				synonym=synonym_list,
				active=active,
				preferredTerm=preferred_term,
			)
			descriptor.save(using='decs_portal')
			self.stdout.write('Successfully saved "%s" Full Qualifier' % identifier_id)

		exec_time = time.time()-start
		self.stdout.write('Execution time "%s"' % time.strftime("%H:%M:%S",time.gmtime(exec_time)))
