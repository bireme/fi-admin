from django_elasticsearch_dsl import Document, fields as fields_dsl
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer

from thesaurus.models import TermListDesc, TermListQualif, PreviousIndexingListDesc, TreeNumbersListDesc, TreeNumbersListQualif

# analizador para palabra a palabra
standard_asciifolding = analyzer(
	'standard_asciifolding',
	tokenizer="standard",
	filter=["lowercase", "asciifolding"]
)
# analizador para campo completo
keyword_asciifolding = analyzer(
	'keyword_asciifolding',
	tokenizer="keyword",
	filter=["lowercase", "asciifolding"]
)


@registry.register_document
class DescriptorTermDocument(Document):
	term_string = fields_dsl.TextField(
		analyzer=standard_asciifolding,
		fields={'full_field': fields_dsl.TextField(analyzer=keyword_asciifolding)}
	)

	# Filter by exact field value: "pt-br", "es-es"
	language_code = fields_dsl.KeywordField()

	# Filter by exact field value: "Y" or "N" instead of "y" or "n"
	record_preferred_term = fields_dsl.KeywordField()

	# identifier_concept.identifier (IdentifierDesc)
	identifier_concept = fields_dsl.ObjectField(properties={
		'pk': fields_dsl.IntegerField(),
		'identifier': fields_dsl.ObjectField(properties={'pk': fields_dsl.IntegerField()})}
	)

	class Index:
		name = 'descriptor_term'

		settings = {
			'number_of_shards': 1,
			'number_of_replicas': 0
		}

	class Django:
		model = TermListDesc

		fields = [
			'term_thesaurus',
			'status',
		]

		# Ignore auto updating of Elasticsearch when a model is saved or deleted:
		ignore_signals = True
		# Don't perform an index refresh after every update (overrides global setting):
		auto_refresh = False
		# Paginate the django queryset used to populate the index with the specified size
		# (by default it uses the database driver's default setting)
		# queryset_pagination = 5000

@registry.register_document
class QualifierTermDocument(Document):
	term_string = fields_dsl.TextField(
		analyzer=standard_asciifolding,
		fields={'full_field': fields_dsl.TextField(analyzer=keyword_asciifolding)}
	)

	# Filter by exact field value: "pt-br", "es-es"
	language_code = fields_dsl.KeywordField()

	# Filter by exact field value: "Y" or "N" instead of "y" or "n"
	record_preferred_term = fields_dsl.KeywordField()

	# identifier_concept.identifier (from IdentifierQualif)
	identifier_concept = fields_dsl.ObjectField(properties={
		'pk': fields_dsl.IntegerField(),
		'identifier': fields_dsl.ObjectField(properties={'pk': fields_dsl.IntegerField()})}
	)

	class Index:
		name = 'qualifier_term'

		settings = {
			'number_of_shards': 1,
			'number_of_replicas': 0
		}

	class Django:
		model = TermListQualif

		fields = [
			'term_thesaurus',
			'status',
		]
		# Ignore auto updating of Elasticsearch when a model is saved or deleted:
		ignore_signals = True
		# Don't perform an index refresh after every update (overrides global setting):
		auto_refresh = False


@registry.register_document
class PreviousTermDocument(Document):

	term_string = fields_dsl.TextField(
		attr="previous_indexing",
		analyzer=standard_asciifolding,
		fields={'full_field': fields_dsl.TextField(analyzer=keyword_asciifolding)}
	)
	"""
	identifier = fields_dsl.ObjectField(properties={
		'descriptor_ui': fields_dsl.TextField(),
		'pk': fields_dsl.IntegerField()
	})
	"""
	# Filter by exact field
	identifier_id = fields_dsl.KeywordField()

	# Filter by exact field value: "pt-br", "es-es"
	language_code = fields_dsl.KeywordField()

	status = fields_dsl.IntegerField()

	term_thesaurus = fields_dsl.IntegerField()

	class Index:
		name = 'previous_term'

		settings = {
			'number_of_shards': 1,
			'number_of_replicas': 0
		}

	def prepare_status(self, instance):
		return 1

	def prepare_term_thesaurus(self, instance):
		return 1

	class Django:
		model = PreviousIndexingListDesc
		# Ignore auto updating of Elasticsearch when a model is saved or deleted:
		ignore_signals = True
		# Don't perform an index refresh after every update (overrides global setting):
		auto_refresh = False


@registry.register_document
class DescriptorTreeNumberDocument(Document):

	# Filter by exact field value: "A01.111"
	tree_number = fields_dsl.KeywordField()

	# Filter by exact field
	#identifier_id = fields_dsl.KeywordField()

	# identifier. (from IdentifierDesc)
	identifier = fields_dsl.ObjectField(properties={
		'pk': fields_dsl.IntegerField(),
		'thesaurus_id': fields_dsl.IntegerField()}
	)

	class Index:
		name = 'descriptor_treenumber'

		settings = {
			'number_of_shards': 1,
			'number_of_replicas': 0
		}

	class Django:
		model = TreeNumbersListDesc
		# Ignore auto updating of Elasticsearch when a model is saved or deleted:
		ignore_signals = True
		# Don't perform an index refresh after every update (overrides global setting):
		auto_refresh = False


@registry.register_document
class QaulifierTreeNumberDocument(Document):

	# Filter by exact field value: "A01.111"
	tree_number = fields_dsl.KeywordField()

	# Filter by exact field
	#identifier_id = fields_dsl.KeywordField()

	# identifier. (from IdentifierDesc)
	identifier = fields_dsl.ObjectField(properties={
		'pk': fields_dsl.IntegerField(),
		'thesaurus_id': fields_dsl.IntegerField()}
	)

	class Index:
		name = 'qualifier_treenumber'

		settings = {
			'number_of_shards': 1,
			'number_of_replicas': 0
		}

	class Django:
		model = TreeNumbersListQualif
		# Ignore auto updating of Elasticsearch when a model is saved or deleted:
		ignore_signals = True
		# Don't perform an index refresh after every update (overrides global setting):
		auto_refresh = False
