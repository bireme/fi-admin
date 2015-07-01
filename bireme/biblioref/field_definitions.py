# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

language_choices = (('pt', 'Português'), ('es', 'Espanhol'), ('en', 'Inglês'))

field_tag_map = {'cooperative_center_code': '01', 'call_number': '03', 'database': '04', 'literature_type': '05',
                 'treatment_level':  '06', 'inventory_number': '07', 'eletronic_address': '08', 'record_type': '09',
                 'individual_author': '10', 'corporate_author': '11', 'title': '12', 'english_translated_title': '13',
                 'pages': '14', 'individual_author_monographic': '16', 'corporate_author_monographic': '17',
                 'title_monographic': '18', 'english_title_monographic': '19', 'pages_monographic': '20',
                 'volume_monographic': '21', 'individual_author_collection': '23', 'corporate_author_collection': '24',
                 'title_collection': '25', 'english_title_collection': '26', 'total_number_of_volumes': '27',
                 'title_serial': '30', 'volume_serial': '31', 'issue_number': '32', 'issn': '35',
                 'thesis_dissertation_leader': '49', 'thesis_dissertation_institution': '50',
                 'thesis_dissertation_academic_title': '51', 'publisher': '62', 'edition': '63', 'publication_city': '66',
                 'symbol': '68', 'isbn': '69', 'descriptive_information': '38', 'text_language': '40',
                 'conference_sponsoring_institution': '52', 'conference_name': '53', 'conference_date': '54',
                 'conference_normalized_date': '55', 'conference_city': '56', 'project_sponsoring_institution': '58',
                 'project_name': '59', 'internal_note': '61', 'publication_date': '64',
                 'publication_date_normalized': '65', 'total_number_of_references': '72',
                 'time_limits_from': '74', 'time_limits_to': '75', 'person_as_subject': '78', 'non_decs_region': '82',
                 'abstract': '83', 'transfer_date_to_database': '84', 'author_keyword': '85',
                 'item_form': '110', 'type_of_computer_file': '111', 'type_of_cartographic_material': '112',
                 'type_of_journal': '113', 'type_of_visual_material': '114', 'specific_designation_of_the_material': '115',
                 'general_note': '500', 'formatted_contents_note': '505', 'additional_physical_form_available_note': '530',
                 'reproduction_note': '533', 'original_version_note': '534', 'institution_as_subject': '610',
                 'local_descriptors': '653', 'clinical_trial_registry_name': '700', 'doi_number': '724'
                 }

other_notes_section = ('other_notes', {'fields': ['general_note', 'formatted_contents_note',
                                       'additional_physical_form_available_note', 'reproduction_note',
                                       'original_version_note', 'internal_note'],
                                       'legend': 'Other notes',
                                       'classes': ['collapse']})

abstract_section = ('abstract', {'fields': ['abstract'],
                                 'legend': 'Abstract',
                                 'classes': ['collapse']})


comp_info_section = ('comp_info', {'fields': ['descriptive_information', 'text_language'],
                                   'legend': 'Complementary Information',
                                   'classes': ['collapse']})

subject_section = ('content_data', {'fields': ['author_keyword'],
                                    'legend': 'Subject',
                                    'classes': ['collapse']})

imprint_section = ('imprint', {'fields': ['publisher', 'edition', 'publication_date',
                                          'publication_date_normalized', 'publication_city',
                                          'symbol', 'isbn'],
                               'legend': 'Imprint',
                               'classes': ['collapse']})

FIELDS_BY_DOCUMENT_TYPE = {}

# Periodical series (source)
FIELDS_BY_DOCUMENT_TYPE['S'] = [('general', {'fields': ['status', 'database'], 'legend': 'General information'}),

                                ('serial_level', {'fields': ['title_serial', 'volume_serial', 'issue_number',
                                                             'issn'],
                                                  'legend': 'Serial level'}),

                                ('imprint', {'fields': ['publication_date', 'publication_date_normalized'],
                                 'legend': 'Imprint'})]


# Periodical series (analytic)
FIELDS_BY_DOCUMENT_TYPE['Sas'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                          'electronic_address', 'record_type', 'item_form',
                                                          'type_of_journal'],
                                               'legend': 'General information'}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': 'Analytic Level'}),

                                  ('comp_info', {'fields': ['descriptive_information', 'text_language', 'doi'],
                                                 'legend': 'Complementary Information',
                                                 'classes': ['collapse']}),

                                  other_notes_section,

                                  ('content_data', {'fields': ['clinical_trial_registry_name', 'author_keyword'],
                                                    'legend': 'Content data',
                                                    'classes': ['collapse']}),

                                  abstract_section
                                  ]

# Monographic (source)
FIELDS_BY_DOCUMENT_TYPE['M'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                        'inventory_number', 'electronic_address', 'record_type',
                                                        'item_form'],
                                             'legend': 'General information'}),

                                ('monographic_level', {'fields': ['individual_author_monographic',
                                                                  'corporate_author_monographic', 'title_monographic',
                                                                  'english_title_monographic', 'pages_monographic',
                                                                  'volume_monographic'],
                                                       'legend': 'Monographic Level'}),

                                comp_info_section,

                                other_notes_section,

                                imprint_section,

                                subject_section,

                                abstract_section
                                ]

# Monographic (analytic)
FIELDS_BY_DOCUMENT_TYPE['Mam'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                          'inventory_number', 'electronic_address', 'record_type',
                                                          'item_form'],
                                               'legend': 'General information'}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': 'Analytic Level'}),

                                  comp_info_section,

                                  other_notes_section,

                                  subject_section,

                                  abstract_section
                                  ]

# Thesis, dissertation (source)
FIELDS_BY_DOCUMENT_TYPE['T'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                        'inventory_number', 'electronic_address', 'record_type'],
                                             'legend': 'General information'}),

                                ('monographic_level', {'fields': ['individual_author_monographic',
                                                                  'title_monographic', 'english_title_monographic',
                                                                  'pages_monographic'],
                                                       'legend': 'Monographic Level'}),

                                comp_info_section,

                                ('thesis_notes', {'fields': ['thesis_dissertation_leader',
                                                             'thesis_dissertation_institution',
                                                             'thesis_dissertation_academic_title'],
                                                  'legend': 'Thesis Notes',
                                                  'classes': ['collapse']}),


                                other_notes_section,

                                imprint_section,

                                subject_section,

                                abstract_section
                                ]

# Thesis, dissertation (analytic)
FIELDS_BY_DOCUMENT_TYPE['Tam'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                          'inventory_number', 'electronic_address', 'record_type',
                                                          'item_form'],
                                               'legend': 'General information'}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': 'Analytic Level'}),

                                  comp_info_section,

                                  ('thesis_notes', {'fields': ['thesis_dissertation_leader'],
                                                    'legend': 'Thesis Notes',
                                                    'classes': ['collapse']}),

                                  other_notes_section,

                                  subject_section,

                                  abstract_section
                                  ]

# Non Conventional (source)
FIELDS_BY_DOCUMENT_TYPE['N'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                        'inventory_number', 'electronic_address', 'record_type'],
                                             'legend': 'General information'}),

                                ('monographic_level', {'fields': ['individual_author_monographic',
                                                                  'corporate_author_monographic',
                                                                  'title_monographic', 'english_title_monographic',
                                                                  'pages_monographic', 'volume_monographic'],
                                                       'legend': 'Monographic Level'}),

                                comp_info_section,

                                other_notes_section,

                                imprint_section,

                                subject_section,

                                abstract_section
                                ]

# Thesis, dissertation (analytic)
FIELDS_BY_DOCUMENT_TYPE['Nam'] = [('general', {'fields': ['source', 'status', 'call_number', 'database',
                                                          'inventory_number', 'electronic_address', 'record_type',
                                                          'item_form'],
                                               'legend': 'General information'}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': 'Analytic Level'}),

                                  comp_info_section,

                                  other_notes_section,

                                  subject_section,

                                  abstract_section
                                  ]


class CallNumberAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Center code'), missing=unicode(''))
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Classification number'), missing=unicode(''))
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Author number'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Volumen, inventory number, part'), missing=unicode(''),)
    _t = colander.SchemaNode(colander.String('utf-8'), title=_('Lending system'), missing=unicode(''),)


class CallNumber(colander.SequenceSchema):
    item = CallNumberAttributes(title=_('Call number'))


class ElectronicAddressAttributes(colander.MappingSchema):
    _u = colander.SchemaNode(colander.String('utf-8'), title=_('Electric address'))
    _i = colander.SchemaNode(colander.String('utf-8'),
                             widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))
    _g = colander.SchemaNode(colander.String('utf-8'), title=_('Fulltext'), missing=unicode(''),)
    _k = colander.SchemaNode(colander.String('utf-8'), title=_('Password'), missing=unicode(''),)
    _l = colander.SchemaNode(colander.String('utf-8'), title=_('Logon'), missing=unicode(''),)
    _q = colander.SchemaNode(colander.String('utf-8'), title=_('File extension'), missing=unicode(''),)
    _s = colander.SchemaNode(colander.String('utf-8'), title=_('File length'), missing=unicode(''),)
    _x = colander.SchemaNode(colander.String('utf-8'), title=_('No public note'), missing=unicode(''),)
    _y = colander.SchemaNode(colander.String('utf-8'), title=_('File type'), missing=unicode(''),)
    _z = colander.SchemaNode(colander.String('utf-8'), title=_('Public note'), missing=unicode(''),)


class ElectronicAddress(colander.SequenceSchema):
    item = ElectronicAddressAttributes(title=_('Electronic address'))


class TitleAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Title'))
    _i = colander.SchemaNode(colander.String('utf-8'),
                             widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))


class Title(colander.SequenceSchema):
    title = TitleAttributes(title=_('Title'))


class IndividualAuthorAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Personal author'))
    _1 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 1'), missing=unicode(''),)
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'), missing=unicode(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'), missing=unicode(''),)


class IndividualAuthor(colander.SequenceSchema):
    item = IndividualAuthorAttributes(title=_('Individual author'))


class IndividualAuthorMonographic(colander.SequenceSchema):
    item = IndividualAuthorAttributes(title=_('Individual author'))


class CorporateAuthorAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Corporate author'))
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Degree of responsibility'), missing=unicode(''),)


class CorporateAuthor(colander.SequenceSchema):
    item = CorporateAuthorAttributes(title=_('Corporate author'))


class CorporateAuthorMonographic(colander.SequenceSchema):
    item = CorporateAuthorAttributes(title=_('Corporate author'))


class DescriptiveInformationAttributes(colander.MappingSchema):
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Other physical details'), missing=unicode(''),)
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Item extension'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Dimension'), missing=unicode(''),)
    _e = colander.SchemaNode(colander.String('utf-8'), title=_('Accompanying material'), missing=unicode(''),)


class DescriptiveInformation(colander.SequenceSchema):
    item = DescriptiveInformationAttributes(title=_('Descriptive information'))


class ThesisDissertationLeaderAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Personal author'))
    _1 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 1'), missing=unicode(''),)
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'), missing=unicode(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'), missing=unicode(''),)


class ThesisDissertationLeader(colander.SequenceSchema):
    item = ThesisDissertationLeaderAttributes(title=_('Leader'))


class AbstractAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Abstract'),
                               widget=deform.widget.TextAreaWidget(rows=15, cols=120))
    _i = colander.SchemaNode(colander.String('utf-8'), widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))


class Abstract(colander.SequenceSchema):
    item = AbstractAttributes(title=_('Abstract'))


class AuthorKeywordAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Keyword'))
    _s = colander.SchemaNode(colander.String('utf-8'), title=_('Qualifier'), missing=unicode(''),)
    _i = colander.SchemaNode(colander.String('utf-8'), widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))


class AuthorKeyword(colander.SequenceSchema):
    item = AuthorKeywordAttributes(title=_('Author keyword'))
