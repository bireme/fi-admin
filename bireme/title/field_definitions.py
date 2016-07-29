# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

language_choices = (('pt', 'Português'), ('es', 'Espanhol'), ('en', 'Inglês'))

field_tag_map = {'local_code': '03', 'record_type': '05', 'treatment_level': '06',
                 'cooperative_center_code': '10', 'national_code': '20', 'id_number': '30',
                 'secs_number': '37', 'related_systems': '40', 'status': '50', 'title': '100',
                 'subtitle': '110', 'section': '120', 'section_title': '130',
                 'responsibility_mention': '140', 'shortened_title': '150',
                 'medline_shortened_title': '180', 'parallel_titles': '230',
                 'shortened_parallel_titles': '235', 'other_titles': '240',
                 'initial_volume': '302', 'initial_number': '303', 'final_date': '304',
                 'final_volume': '305', 'final_number': '306', 'country': '310', 'state': '320',
                 'publication_level': '330', 'title_alphabet': '340', 'text_language': '350',
                 'abstract_language': '360', 'frequency': '380', 'issn': '400', 'coden': '410',
                 'medline_code': '420', 'classification': '430', 'thematic_area': '435',
                 'bvs_specialties': '436', 'descriptors': '440', 'users': '445',
                 'index_range': '450', 'acquisition_form': '460', 'acquisition_priority': '470',
                 'comercial_editor': '480', 'city': '490', 'lilacs_index_year': '500',
                 'has_edition': '510', 'is_edition': '520', 'has_subseries': '530',
                 'is_subseries': '540', 'has_supplement': '550', 'is_supplement': '560',
                 'continuation': '610', 'partial_continuation': '620', 'absorbed': '650',
                 'absorbed_in_part': '660', 'subdivision': '670', 'fusion': '680',
                 'continued_by': '710', 'continued_in_part_by': '720', 'absorbed_by': '750',
                 'absorbed_in_part_by': '760', 'subdivided': '770', 'merged': '780',
                 'to_form': '790', 'online_notes': '880', 'notes': '900', 'bireme_notes': '910', 'indexer_cc_code': '920', 'editor_cc_code': '930', 'creation_date': '940',
                 'last_change_date': '941', 'online': '999'
                }
