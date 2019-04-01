# coding: utf-8

'''
QUALIFIERS
'''

from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

language_choices = (('pt', 'Português'), ('es', 'Espanhol'), ('en', 'Inglês'))

field_tag_map = {
                'identifier': '776',

                'term_string_en': '001',
                'term_string_es': '002',
                'term_string_pt_br': '003',
                'term_string_es_es': '004',
                'term_string_fr': '016',

                'scope_note_en': '005',
                'scope_note_es': '006',
                'scope_note_pt_br': '007',
                'scope_note_es_es': '008',

                'tree_number': '010',
                'tree_number_201': '201',

                # Usado para mostrar EntryVersion
                # en
                'entry_version_en': '011',

                # es
                'entry_version_es': '012',

                # pt-br
                'entry_version_pt_br': '013',

                'abbreviation': '014',

                # Usado para mostrar UPs do conceito preferido
                'term_string_print_entries_en': '050', # ^i
                'term_string_print_entries_es': '050', # ^e
                'term_string_print_entries_pt_br': '050', # ^p
                'term_string_print_entries_es_es': '050', # ^s
                'term_string_print_entries_fr': '050', # ^f

                # Usado para mostrar UPs de conceitos nao preferidos
                'term_string_print_entries_en_NP': '050', # ^i
                'term_string_print_entries_es_NP': '050', # ^e
                'term_string_print_entries_pt_br_NP': '050', # ^p
                'term_string_print_entries_es_es_NP': '050', # ^s
                'term_string_print_entries_fr_NP': '050', # ^f

                'decs_code': '099',

                'record_type': '105',

                ### 106
                # # c
                # pre_codificado
                'descriptor_type_pre_codificado': '106',

                # # d
                # desastre
                'descriptor_type_desastre': '106',

                # # f
                # reforma_saude
                'descriptor_type_reforma_saude': '106',

                # # g
                # geografico
                'descriptor_type_geografico': '106',

                # # h
                # mesh
                'descriptor_type_mesh': '106',

                # # l
                # pt_lilacs
                'descriptor_type_pt_lilacs': '106',

                # # n
                # nao_indexavel
                'descriptor_type_nao_indexavel': '106',

                # # p
                # homeopatia
                'descriptor_type_homeopatia': '106',

                # # r
                # repidisca
                'descriptor_type_repidisca': '106',

                # # s
                # saude_publica
                'descriptor_type_saude_publica': '106',

                # # x
                # exploded
                'descriptor_type_exploded': '106',

                # # z
                # geog_decs
                'descriptor_type_geog_decs': '106',

                'annotation_en': '110', 
                'online_note_en': '117',
                'history_note_en': '119',

                'annotation_es': '210',
                'online_note_es': '217',
                'history_note_es': '219',

                'annotation_pt_br': '310',
                'online_note_pr_br': '317',
                'history_note_pt_br': '319',

                'mesh_id_qualifier_ui': '480',

                'allowed_qualifiers': '950',

                }
