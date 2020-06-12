# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from main.models import SourceLanguage
from utils.models import AuxCode, Country

import colander
import deform
import json

language_choices = [('', '')] + [(aux.code, aux) for aux in AuxCode.objects.filter(field='text_language')]

field_tag_map = {'cooperative_center_code': '01', 'id': '02', 'call_number': '03', 'database': '04', 'literature_type': '05',
                 'treatment_level':  '06', 'inventory_number': '07', 'electronic_address': '08', 'record_type': '09',
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
                 'project_name': '59', 'internal_note': '61', 'publication_date': '64', 'publication_country': '67',
                 'publication_date_normalized': '65', 'publication_type': '71', 'total_number_of_references': '72',
                 'time_limits_from': '74', 'time_limits_to': '75', 'check_tags': '76', 'person_as_subject': '78', 'non_decs_region': '82',
                 'abstract': '83', 'transfer_date_to_database': '84', 'author_keyword': '85', 'descriptors_primary': '87',
                 'descriptors_secondary': '88', 'item_form': '110', 'type_of_computer_file': '111', 'type_of_cartographic_material': '112',
                 'type_of_journal': '113', 'type_of_visual_material': '114', 'specific_designation_of_the_material': '115',
                 'general_note': '500', 'formatted_contents_note': '505', 'additional_physical_form_available_note': '530',
                 'reproduction_note': '533', 'original_version_note': '534', 'institution_as_subject': '610',
                 'local_descriptors': '653', 'clinical_trial_registry_name': '700', 'doi_number': '724',
                 'source_control': '98', 'export_control_1': '776', 'export_control_2': '778', 'alternate_ids': '779',
                 'created_time': '91', 'created_by': '92', 'updated_time': '93', 'system_version': '899', 'indexed_database': '904',
                 }


indexed_databases = ('indexed_database', {'fields': ['LILACS_indexed', 'indexed_database', 'BIREME_reviewed'],
                                          'legend': _('Indexed databases')})

other_notes_section = ('other_notes', {'fields': ['general_note', 'formatted_contents_note',
                                       'additional_physical_form_available_note', 'reproduction_note',
                                       'original_version_note'],
                                       'legend': _('Other notes'),
                                       'classes': ['collapse']})

abstract_section = ('abstract', {'fields': ['abstract'],
                                 'legend': _('Abstract'),
                                 'classes': ['collapse']})


comp_info_section = ('comp_info', {'fields': ['descriptive_information', 'text_language'],
                                   'legend': _('Complementary Information'),
                                   'classes': ['collapse']})

comp_info_section_doi = ('comp_info', {'fields': ['descriptive_information', 'text_language', 'doi_number'],
                                       'legend': _('Complementary Information'),
                                       'classes': ['collapse']})


subject_section = ('content_data', {'fields': ['author_keyword'],
                                    'legend': _('Subject'),
                                    'classes': ['collapse']})

indexing_section = ('indexing', {'fields': ['publication_type', 'check_tags', 'time_limits_from', 'time_limits_to',
                                 'person_as_subject', 'non_decs_region', 'institution_as_subject', 'total_number_of_references'],
                                 'legend': _('Additional indexing fields')})


imprint_section = ('imprint', {'fields': ['publisher', 'edition', 'publication_date',
                                          'publication_date_normalized', 'publication_city',
                                          'publication_country', 'symbol', 'isbn'],
                               'legend': _('Imprint'),
                               'classes': ['collapse']})

fulltext_section = ('fulltext', {'fields': ['electronic_address'],
                                 'legend': _('Fulltext'),
                                 })


monographic_section = ('monographic_level', {'fields': ['individual_author_monographic',
                                                        'corporate_author_monographic', 'title_monographic',
                                                        'english_title_monographic', 'pages_monographic',
                                                        'volume_monographic'],
                                             'legend': _('Monographic Level')
                                             })


collection_section = ('collection_level', {'fields': ['individual_author_collection', 'corporate_author_collection',
                                                      'title_collection', 'english_title_collection', 'total_number_of_volumes'],
                                           'legend': _('Collection level'),
                                           })

serial_section = ('serial_level', {'fields': ['title_serial', 'issn', 'volume_serial',
                                              'issue_number'],
                                   'legend': _('Serial level')})

thesis_notes = ('thesis_notes', {'fields': ['thesis_dissertation_leader',
                                            'thesis_dissertation_institution',
                                            'thesis_dissertation_academic_title'],
                                 'legend': _('Thesis Notes'),
                                 'classes': ['collapse']})


FIELDS_BY_DOCUMENT_TYPE = {}

# Periodical series (source)
FIELDS_BY_DOCUMENT_TYPE['S'] = [('general', {'fields': ['status', 'LILACS_indexed', 'BIREME_reviewed'],
                                'legend': _('General information')}),

                                ('serial_level', {'fields': ['title_serial', 'issn', 'volume_serial',
                                                             'issue_number'],
                                                  'legend': _('Serial level')}),

                                ('imprint', {'fields': ['publication_date', 'publication_date_normalized'],
                                 'legend': _('Imprint')})]


# Periodical series (analytic)
FIELDS_BY_DOCUMENT_TYPE['Sas'] = [indexed_databases,
                                  ('general', {'fields': ['source', 'status', 'record_type', 'item_form',
                                                          'type_of_computer_file',
                                                          'type_of_cartographic_material', 'type_of_journal',
                                                          'type_of_visual_material', 'specific_designation_of_the_material'],
                                               'legend': _('General information')}),



                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': _('Analytic Level')}),

                                  ('comp_info', {'fields': ['descriptive_information', 'text_language', 'doi_number'],
                                                 'legend': _('Complementary Information'),
                                                 'classes': ['collapse']}),

                                  other_notes_section,

                                  ('content_data', {'fields': ['clinical_trial_registry_name', 'author_keyword'],
                                                    'legend': _('Content data'),
                                                    'classes': ['collapse']}),

                                  abstract_section,

                                  indexing_section,

                                  fulltext_section,
                                  ]

# Monographic (source)
FIELDS_BY_DOCUMENT_TYPE['Mm'] = [indexed_databases,
                                 ('general', {'fields': ['source', 'status', 'record_type',
                                                         'item_form', 'type_of_computer_file',
                                                         'type_of_cartographic_material', 'type_of_journal',
                                                         'type_of_visual_material', 'specific_designation_of_the_material'],
                                              'legend': _('General information')}),

                                 monographic_section,

                                 comp_info_section_doi,

                                 other_notes_section,

                                 imprint_section,

                                 subject_section,

                                 abstract_section,

                                 indexing_section,

                                 fulltext_section,
                                 ]

# Monographic (analytic)
FIELDS_BY_DOCUMENT_TYPE['Mam'] = [indexed_databases,
                                  ('general', {'fields': ['source', 'status', 'record_type',
                                                          'item_form', 'type_of_computer_file',
                                                          'type_of_cartographic_material', 'type_of_journal',
                                                          'type_of_visual_material', 'specific_designation_of_the_material'],
                                               'legend': _('General information')}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': _('Analytic Level')}),

                                  comp_info_section_doi,

                                  other_notes_section,

                                  subject_section,

                                  abstract_section,

                                  indexing_section,

                                  fulltext_section,

                                  ]

# Collection (source)
FIELDS_BY_DOCUMENT_TYPE['Mc'] = [indexed_databases,
                                 ('general', {'fields': ['source', 'status', 'record_type',
                                                         'item_form', 'type_of_computer_file',
                                                         'type_of_cartographic_material', 'type_of_journal',
                                                         'type_of_visual_material', 'specific_designation_of_the_material'],
                                              'legend': _('General information')}),

                                 collection_section,

                                 comp_info_section,

                                 other_notes_section,

                                 imprint_section,

                                 subject_section,

                                 abstract_section,

                                 indexing_section,

                                 fulltext_section,
                                 ]


# Thesis, dissertation (source)
FIELDS_BY_DOCUMENT_TYPE['Tm'] = [indexed_databases,
                                 ('general', {'fields': ['source', 'status', 'record_type',
                                                         'item_form', 'type_of_computer_file',
                                                         'type_of_cartographic_material', 'type_of_journal',
                                                         'type_of_visual_material', 'specific_designation_of_the_material'],
                                              'legend': _('General information')}),

                                 ('monographic_level', {'fields': ['individual_author_monographic',
                                                                   'title_monographic', 'english_title_monographic',
                                                                   'pages_monographic'],
                                                        'legend': _('Monographic Level')}),

                                 comp_info_section,

                                 thesis_notes,

                                 other_notes_section,

                                 imprint_section,

                                 subject_section,

                                 abstract_section,

                                 indexing_section,

                                 fulltext_section,
                                 ]

# Thesis, dissertation (analytic)
FIELDS_BY_DOCUMENT_TYPE['Tam'] = [indexed_databases,
                                  ('general', {'fields': ['source', 'status', 'record_type',
                                                          'item_form', 'type_of_computer_file',
                                                          'type_of_cartographic_material', 'type_of_journal',
                                                          'type_of_visual_material', 'specific_designation_of_the_material'],
                                               'legend': _('General information')}),

                                  ('analytic_level', {'fields': ['individual_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': _('Analytic Level')}),

                                  comp_info_section,

                                  ('thesis_notes', {'fields': ['thesis_dissertation_analytic_leader'],
                                                    'legend': _('Thesis Notes'),
                                                    'classes': ['collapse']}),

                                  other_notes_section,

                                  subject_section,

                                  abstract_section,

                                  indexing_section,

                                  fulltext_section,
                                  ]

# Non Conventional (source)
FIELDS_BY_DOCUMENT_TYPE['Nm'] = [indexed_databases,
                                 ('general', {'fields': ['source', 'status', 'record_type',
                                                         'item_form', 'type_of_computer_file',
                                                         'type_of_cartographic_material', 'type_of_journal',
                                                         'type_of_visual_material', 'specific_designation_of_the_material'],
                                              'legend': _('General information')}),

                                 monographic_section,

                                 comp_info_section_doi,

                                 other_notes_section,

                                 imprint_section,

                                 subject_section,

                                 abstract_section,

                                 indexing_section,

                                 fulltext_section,
                                 ]

# Non Conventional (analytic)
FIELDS_BY_DOCUMENT_TYPE['Nam'] = [indexed_databases,
                                  ('general', {'fields': ['source', 'status', 'record_type',
                                                          'item_form', 'type_of_computer_file',
                                                          'type_of_cartographic_material', 'type_of_journal',
                                                          'type_of_visual_material', 'specific_designation_of_the_material'],
                                               'legend': _('General information')}),

                                  ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                 'english_translated_title', 'pages'],
                                                      'legend': _('Analytic Level')}),

                                  comp_info_section_doi,

                                  other_notes_section,

                                  subject_section,

                                  abstract_section,

                                  indexing_section,

                                  fulltext_section,
                                  ]


# Monograph in a Collection (source)
FIELDS_BY_DOCUMENT_TYPE['Mmc'] = [indexed_databases,
                                  ('general', {'fields': ['source', 'status', 'record_type',
                                                          'item_form', 'type_of_computer_file',
                                                          'type_of_cartographic_material', 'type_of_journal',
                                                          'type_of_visual_material', 'specific_designation_of_the_material'],
                                               'legend': _('General information')}),

                                  collection_section,

                                  monographic_section,

                                  comp_info_section,

                                  other_notes_section,

                                  imprint_section,

                                  subject_section,

                                  abstract_section,

                                  indexing_section,

                                  fulltext_section,
                                  ]


# Monograph in a Collection (analytic)
FIELDS_BY_DOCUMENT_TYPE['Mamc'] = [indexed_databases,
                                   ('general', {'fields': ['source', 'status', 'record_type',
                                                           'item_form', 'type_of_computer_file',
                                                           'type_of_cartographic_material', 'type_of_journal',
                                                           'type_of_visual_material', 'specific_designation_of_the_material'],
                                                'legend': _('General information')}),

                                   ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                  'english_translated_title', 'pages'],
                                                       'legend': _('Analytic Level')}),

                                   comp_info_section,

                                   other_notes_section,

                                   subject_section,

                                   abstract_section,

                                   indexing_section,

                                   fulltext_section,

                                   ]

# Thesis, Dissertation appearing as a Monograph Series (source)
FIELDS_BY_DOCUMENT_TYPE['TSms'] = [indexed_databases,
                                   ('general', {'fields': ['source', 'status', 'record_type',
                                                           'item_form', 'type_of_computer_file',
                                                           'type_of_cartographic_material', 'type_of_journal',
                                                           'type_of_visual_material', 'specific_designation_of_the_material'],
                                                'legend': _('General information')}),

                                   serial_section,

                                   ('monographic_level', {'fields': ['individual_author_monographic',
                                                                     'title_monographic', 'english_title_monographic',
                                                                     'pages_monographic'],
                                                          'legend': _('Monographic Level')}),

                                   comp_info_section,

                                   thesis_notes,

                                   other_notes_section,

                                   imprint_section,

                                   subject_section,

                                   abstract_section,

                                   indexing_section,

                                   fulltext_section,
                                   ]

# Thesis, Dissertation appearing as a Monograph Series (analytic)
FIELDS_BY_DOCUMENT_TYPE['TSams'] = [indexed_databases,
                                    ('general', {'fields': ['source', 'status', 'record_type',
                                                            'item_form', 'type_of_computer_file',
                                                            'type_of_cartographic_material', 'type_of_journal',
                                                            'type_of_visual_material', 'specific_designation_of_the_material'],
                                                 'legend': _('General information')}),

                                    ('analytic_level', {'fields': ['individual_author', 'title',
                                                                   'english_translated_title', 'pages'],
                                                        'legend': _('Analytic Level')}),

                                    comp_info_section,

                                    ('thesis_notes', {'fields': ['thesis_dissertation_analytic_leader'],
                                                      'legend': _('Thesis Notes'),
                                                      'classes': ['collapse']}),

                                    other_notes_section,

                                    subject_section,

                                    abstract_section,

                                    indexing_section,

                                    fulltext_section,
                                    ]

# Monograph Series (source)
FIELDS_BY_DOCUMENT_TYPE['MSms'] = [indexed_databases,
                                   ('general', {'fields': ['source', 'status', 'record_type',
                                                           'item_form', 'type_of_computer_file',
                                                           'type_of_cartographic_material', 'type_of_journal',
                                                           'type_of_visual_material', 'specific_designation_of_the_material'],
                                                'legend': _('General information')}),

                                   serial_section,

                                   ('monographic_level', {'fields': ['individual_author_monographic',
                                                                     'corporate_author_monographic', 'title_monographic',
                                                                     'english_title_monographic', 'pages_monographic'],
                                                          'legend': _('Monographic Level')}),

                                   comp_info_section,

                                   other_notes_section,

                                   imprint_section,

                                   subject_section,

                                   abstract_section,

                                   indexing_section,

                                   fulltext_section,
                                   ]

# Monograph Series (analytic)
FIELDS_BY_DOCUMENT_TYPE['MSams'] = [('general', {'fields': ['source', 'status', 'LILACS_indexed', 'BIREME_reviewed',
                                                            'record_type', 'item_form', 'type_of_computer_file',
                                                            'type_of_cartographic_material', 'type_of_journal',
                                                            'type_of_visual_material', 'specific_designation_of_the_material'],
                                                 'legend': _('General information')}),

                                    ('analytic_level', {'fields': ['individual_author', 'corporate_author', 'title',
                                                                   'english_translated_title', 'pages'],
                                                        'legend': _('Analytic Level')}),

                                    comp_info_section,

                                    other_notes_section,

                                    subject_section,

                                    abstract_section,

                                    indexing_section,

                                    fulltext_section,
                                    ]



def get_aux_country_list():
    country_list = [('', '')]
    country_list_latin_caribbean = [(c.code, c) for c in Country.objects.filter(LA_Caribbean=True)]
    country_list_other = [(c.code, c) for c in Country.objects.filter(LA_Caribbean=False)]

    country_list.extend([(' ', _('-- Latin America & Caribbean --'))])
    country_list.extend(country_list_latin_caribbean)
    country_list.extend([(' ', _('-- Others --'))])
    country_list.extend(country_list_other)

    return country_list


class CallNumberAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Center code'), missing=unicode(''))
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Classification number'), missing=unicode(''))
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Author number'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Volumen, inventory number, part'), missing=unicode(''),)
    _t = colander.SchemaNode(colander.String('utf-8'), title=_('Lending system'), missing=unicode(''),)


class CallNumber(colander.SequenceSchema):
    item = CallNumberAttributes(title=_('Call number'))


class ElectronicAddressAttributes(colander.MappingSchema):
    file_type_choices = [('', '')]
    file_type_choices.extend([(aux.code.encode('utf-8'), aux) for aux in
                             AuxCode.objects.filter(field='electronic_address_y')])

    file_extension_choices = [('', '')]
    file_extension_choices.extend([(aux.code, aux) for aux in
                                  AuxCode.objects.filter(field='electronic_address_q')])

    _u = colander.SchemaNode(colander.String('utf-8'), title=_('Electronic address'))
    _g = colander.SchemaNode(colander.Boolean(),
                             widget=deform.widget.CheckboxWidget(),
                             label=_('Fulltext'), missing=unicode(''), title='')
    _i = colander.SchemaNode(colander.String('utf-8'),
                             widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))
    _y = colander.SchemaNode(colander.String('utf-8'),
                             widget=deform.widget.SelectWidget(values=file_type_choices),
                             title=_('File type'))
    _q = colander.SchemaNode(colander.String('utf-8'),
                             widget=deform.widget.SelectWidget(values=file_extension_choices),
                             title=_('File extension'))

    _k = colander.SchemaNode(colander.String('utf-8'), title=_('Password'), missing=unicode(''),)
    _l = colander.SchemaNode(colander.String('utf-8'), title=_('Logon'), missing=unicode(''),)
    _s = colander.SchemaNode(colander.String('utf-8'), title=_('File length'), missing=unicode(''),)
    _x = colander.SchemaNode(colander.String('utf-8'), title=_('No public note'), missing=unicode(''),)
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


class TitleMonographic(colander.SequenceSchema):
    title = TitleAttributes(title=_('Title'))


class TitleCollection(colander.SequenceSchema):
    title = TitleAttributes(title=_('Title'))


class IndividualAuthorAttributes(colander.MappingSchema):
    def validate_author(form, value):
        if value != 'Anon':
            if not ',' in value:
                exc = colander.Invalid(form, _("Comma abscent"))
                raise exc
            elif not ', ' in value:
                exc = colander.Invalid(form, _("Insert space after comma"))
                raise exc


    degree_choices = [('', '')]
    degree_choices.extend([(aux.code, aux) for aux in
                          AuxCode.objects.filter(field='degree_of_responsibility')])

    countries_choices = get_aux_country_list()

    text = colander.SchemaNode(colander.String('utf-8'), title=_('Personal author'), validator=validate_author,
                               description=_('Format: Lastname, Name'))
    _1 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 1'), missing=unicode(''),)
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation city'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'),
                             widget=deform.widget.SelectWidget(values=countries_choices), missing=unicode(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'),
                             widget=deform.widget.SelectWidget(values=degree_choices),
                             missing=unicode(''),)


class IndividualAuthor(colander.SequenceSchema):
    item = IndividualAuthorAttributes(title=_('Individual author'))


class IndividualAuthorMonographic(colander.SequenceSchema):
    item = IndividualAuthorAttributes(title=_('Individual author'))


class IndividualAuthorCollection(colander.SequenceSchema):
    item = IndividualAuthorAttributes(title=_('Individual author'))


class CorporateAuthorAttributes(colander.MappingSchema):
    degree_choices = [('', '')]
    degree_choices.extend([(aux.code, aux) for aux in
                          AuxCode.objects.filter(field='degree_of_responsibility')])

    text = colander.SchemaNode(colander.String('utf-8'), title=_('Corporate author'))
    _r = colander.SchemaNode(colander.String('utf-8'),
                             title=_('Degree of responsibility'),
                             widget=deform.widget.SelectWidget(values=degree_choices),
                             missing=unicode(''),)


class CorporateAuthor(colander.SequenceSchema):
    item = CorporateAuthorAttributes(title=_('Corporate author'))


class CorporateAuthorMonographic(colander.SequenceSchema):
    item = CorporateAuthorAttributes(title=_('Corporate author'))


class CorporateAuthorCollection(colander.SequenceSchema):
    item = CorporateAuthorAttributes(title=_('Corporate author'))


class DescriptiveInformationAttributes(colander.MappingSchema):
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Other physical details'), missing=unicode(''),)
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Item extension'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Dimension'), missing=unicode(''),)
    _e = colander.SchemaNode(colander.String('utf-8'), title=_('Accompanying material'), missing=unicode(''),)


class DescriptiveInformation(colander.SequenceSchema):
    item = DescriptiveInformationAttributes(title=_('Descriptive information'))


class ThesisDissertationLeaderAttributes(colander.MappingSchema):
    countries_choices = get_aux_country_list()

    text = colander.SchemaNode(colander.String('utf-8'), title=_('Leader'))
    _1 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 1'), missing=unicode(''),)
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation city'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'),
                             widget=deform.widget.SelectWidget(values=countries_choices), missing=unicode(''),)


class ThesisDissertationLeader(colander.SequenceSchema):
    item = ThesisDissertationLeaderAttributes(title=_('Leader'))

class ThesisDissertationAnalyticLeader(colander.SequenceSchema):
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


class PagesAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Pages'), missing=unicode(''),)
    _f = colander.SchemaNode(colander.String('utf-8'), title=_('Initial number'), missing=unicode(''),)
    _l = colander.SchemaNode(colander.String('utf-8'), title=_('End number'), missing=unicode(''),)
    _e = colander.SchemaNode(colander.String('utf-8'), title=_('Electronic location identifier'), missing=unicode(''),)


class Pages(colander.SequenceSchema):
    pages = PagesAttributes(title=_('Pages'))


class ClinicalTrialRegistryNameAttributes(colander.MappingSchema):
    db_choices = [(aux.code, aux) for aux in
                  AuxCode.objects.filter(field='clinical_trial_database')]

    text = colander.SchemaNode(colander.String('utf-8'), title=_('Database'),
                               widget=deform.widget.SelectWidget(values=db_choices))
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Record number'))
    _u = colander.SchemaNode(colander.String('utf-8'), title=_('URL'), missing=unicode(''),)

class ClinicalTrialRegistryName(colander.SequenceSchema):
    item = ClinicalTrialRegistryNameAttributes(title=_('Clinical Trial'))
