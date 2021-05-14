#! coding: utf-8
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _, get_language
from django.utils.translation import ugettext as __
from django.utils.translation import string_concat
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django import forms
from form_utils.forms import BetterModelForm, FieldsetCollection
from django.conf import settings

from main.models import Descriptor
from utils.forms import BaseDescriptorInlineFormSet
from utils.templatetags.app_filters import fieldtype
from title.models import Title, IndexRange
from utils.models import AuxCode
from attachments.models import Attachment
from database.models import Database

from models import *
import json
import simplejson
import requests
import re


class SelectDocumentTypeForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = (
        ('S', _('Journals (Periodical Series)')),
        ('Mm', _('Monograph')),
        ('Tm', _('Thesis/Dissertation')),
        ('Mmc', _('Monograph in a Collection')),
        ('Mc', _('Collection of Monographs')),
        ('MSms', _('Monograph Series')),
        ('Nm', _('Non conventional')),
        ('TSms', _('Thesis/Dissertation appearing as a Monograph Series')),
    )

    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES, label=_('Select document type'))
    document_type.widget.attrs['class'] = 'input-xlarge'


class BiblioRefForm(BetterModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)
        self.document_type = kwargs.pop('document_type', None)
        self.reference_source = kwargs.pop('reference_source')
        self.user_role = self.user_data['service_role'].get('LILDBI', 'doc')
        self.is_LILACS = False

        fieldsets = kwargs.pop('fieldsets', None)

        super(BiblioRefForm, self).__init__(*args, **kwargs)

        # used for fieldsets method for construct internal fieldset_collection
        self._fieldsets = fieldsets

        # hidden status field for documentalist and llxp editor profile
        if self.user_role == 'doc' or self.user_role == 'editor_llxp':
            self.fields['status'].widget = widgets.HiddenInput()

        # hidden not necessary fields for llxp editor profile
        if self.user_role == 'editor_llxp':
            # hide LILACS_indexed field
            self.fields['LILACS_indexed'].widget = widgets.HiddenInput()
            # source
            if self.document_type == 'S':
                self.fields['issn'].widget = widgets.HiddenInput()
            # analytic
            else:
                self.fields['record_type'].widget = widgets.HiddenInput()
                self.fields['item_form'].widget = widgets.HiddenInput()
                self.fields['type_of_journal'].widget = widgets.HiddenInput()
                self.fields['english_translated_title'].widget = widgets.HiddenInput()

        # hide BIREME reviewed field for non BIREME users
        if self.user_data['user_cc'] != 'BR1.1':
            self.fields['BIREME_reviewed'].widget = widgets.HiddenInput()

        # hide unnecessary fields of thesis
        if self.document_type == 'Tm':
            self.fields['publisher'].widget = widgets.HiddenInput()
            self.fields['isbn'].widget = widgets.HiddenInput()

        # load serial titles for serial analytic
        if self.document_type == 'S' and not self.reference_source:
            title_objects = Title.objects.all()

            # populate choice title list based on user profile
            if self.user_role == 'editor_llxp':
                # for LILACS Express editor return only serials with same editor_cc_code of current user
                titles_from_this_editor = title_objects.filter(editor_cc_code=self.user_data['user_cc']).exclude(indexer_cc_code='')
                titles_from_this_editor = titles_from_this_editor.order_by('shortened_title')
                title_list = [(t.shortened_title, "%s|%s" % (t.shortened_title, t.issn)) for t in titles_from_this_editor]
            else:
                # for regular users return a title list splited in two parts:
                # 1- journals that is indexed by the user center code using index range relation model
                cc_code = self.user_data['user_cc']
                titles_indexed_by_this_cc = title_objects.filter(indexrange__indexer_cc_code=cc_code).order_by('shortened_title').distinct()

                # 2- titles that has indexed by other centers
                # -exclude titles that has not records in indexrange and then exclude titles from the current cc (alread listed in titles_indexed_by_this_cc)
                titles_indexed_by_others = title_objects.exclude(indexrange__isnull=True).exclude(indexrange__indexer_cc_code=cc_code)
                # -filter by titles thas has at least one indexer_cc_code (diff from empty string)
                titles_indexed_by_others = titles_indexed_by_others.filter(indexrange__indexer_cc_code__gt='').distinct()
                # -sort by short title
                titles_indexed_by_others = titles_indexed_by_others.order_by('shortened_title')

                title_list = []
                title_list_indexer_code = [(t.shortened_title, "%s|%s" % (t.shortened_title, t.issn)) for t in titles_indexed_by_this_cc]
                title_list_other = [(t.shortened_title, "%s|%s" % (t.shortened_title, t.issn)) for t in titles_indexed_by_others]

                separator = u' ────────── '
                label_indexed = separator + __('Indexed by your cooperative center') + separator
                label_not_indexed = separator + __('Indexed by other cooperative centers') + separator

                if title_list_indexer_code:
                    title_list.extend([('', label_indexed)])
                    title_list.extend(title_list_indexer_code)
                    title_list.extend([('', '')])
                title_list.extend([('', label_not_indexed)])
                title_list.extend(title_list_other)

            self.fields['title_serial'] = forms.ChoiceField(choices=title_list, required=False)
            self.fields['title_serial_other'] = forms.CharField(required=False)

        if 'publication_country' in self.fields:
            # divide list of countries in Latin America & Caribbean and Others
            country_list = [('', '')]
            country_list_latin_caribbean = [(c.pk, unicode(c)) for c in Country.objects.filter(LA_Caribbean=True)]
            country_list_other = [(c.pk, unicode(c)) for c in Country.objects.filter(LA_Caribbean=False)]

            # sort list by translation name
            country_list_latin_caribbean.sort(key=lambda c: c[1])
            country_list_other.sort(key=lambda c: c[1])

            separator = "-----------"
            label_latin_caribbean = separator + __('Latin America & Caribbean') + separator
            label_other = separator + __('Others') + separator

            country_list.extend([('', label_latin_caribbean)])
            country_list.extend(country_list_latin_caribbean)
            country_list.extend([('', label_other)])
            country_list.extend(country_list_other)

            self.fields['publication_country'].choices = country_list

        if 'indexed_database' in self.fields:
            regional_indexes = Database.objects.filter(regional_index=True)
            # populate field option with all regional indexes
            self.fields['indexed_database'].choices = [(db.pk, unicode(db)) for db in regional_indexes]

            # if is a new article search in Title for indexes (databases) that index the article journal
            if self.document_type == 'Sas' and not self.instance.pk:
                selected_indexes = []
                # get article source title
                title_source = self.reference_source.title_serial
                # get title detail
                try:
                    title_record = Title.objects.get(shortened_title=title_source)
                except Title.DoesNotExist:
                    title_record = None
                # if title found retrieve databases that index the title
                if title_record:
                    # get indexes (databases) where title is indexed. Filter by final date empty = status current
                    title_index_list = IndexRange.objects.filter(title=title_record, final_date='')
                    # create a acronym list for compare
                    title_acronym_list = [idx.index_code.name  for idx in title_index_list]

                    # check if index is present in title index list
                    for idx in regional_indexes:
                        # if title is indexed by database append
                        if idx.acronym in title_acronym_list:
                            selected_indexes.append(str(idx.pk))

                    # automatic mark current article with indexes where journal are indexed
                    if selected_indexes:
                        self.initial['indexed_database'] = selected_indexes

    def fieldsets(self):
        if not self._fieldset_collection:
            self._fieldset_collection = FieldsetCollection(self, self._fieldsets)

        return self._fieldset_collection

    def is_visiblefield(self, fieldname):
        # return a list of lists.
        list_of_fields = [value['fields'] for item, value in self._fieldsets]
        # change list of lists flatt
        find_list = [val for sublist in list_of_fields for val in sublist]

        # check if field is at fieldset
        is_visible = fieldname in find_list
        if is_visible:
            field = self.fields[fieldname]
            # check if field is not hidden
            if field.widget.is_hidden and not fieldtype(field) == 'JSONFormField':
                is_visible = False

        return is_visible

    def check_pontuation(self, pontuation, value, field, message_item):
        pontuation_with_space_after = "%s " % pontuation
        pontuation_with_space_before = " %s" % pontuation

        if pontuation in value:
            if not pontuation_with_space_after in value:
                message = _("Insert space after %s") % pontuation
                message = string_concat(message_item, message)
                self.add_error(field, message)
            if pontuation_with_space_before in value:
                message = _("Delete space before %s") % pontuation
                message = string_concat(message_item, message)
                self.add_error(field, message)

    def check_all_pontuation(self, value, field, message_item=''):
        pontuation_list = [',', ';', '.', ':']

        for pontuation in pontuation_list:
            self.check_pontuation(pontuation, value, field, message_item)

    def check_author_presence(self, data, field_individual, field_corporate):
        # check presence of individual and corporate author
        if data.get(field_individual) and data.get(field_corporate):
            self.add_error(field_individual, _("Individual Author and Corporate Autor present simultaneous"))
        else:
            if not data.get(field_individual) and not data.get(field_corporate):
                self.add_error(field_individual, _("Individual Author or Corporate Author mandatory"))

    def clean(self):
        data = self.cleaned_data
        status = self.cleaned_data.get('status')
        error_messages = []

        # only apply checks when status is published
        if status == 1:
            for field_name, field_value in self.fields.iteritems():
                field_check = data.get(field_name)

                if isinstance(self.fields[field_name].widget, forms.widgets.Textarea):
                    if '%' in field_check:
                        self.add_error(field_name, _("The % simbol don't separete occurences"))

                if isinstance(field_check, basestring):
                    if field_check.strip().endswith('.'):
                        self.add_error(field_name, _("Point at end of field is not allowed"))

            if self.is_visiblefield('individual_author') and self.is_visiblefield('corporate_author'):
                self.check_author_presence(data, 'individual_author', 'corporate_author')

            if self.is_visiblefield('individual_author_monographic') and self.is_visiblefield('corporate_author_monographic'):
                self.check_author_presence(data, 'individual_author_monographic', 'corporate_author_monographic')

            if self.is_visiblefield('individual_author_collection') and self.is_visiblefield('corporate_author_collection'):
                self.check_author_presence(data, 'individual_author_collection', 'corporate_author_collection')

            if self.is_visiblefield('issue_number') and self.document_type[0] == 'S':
                if not data.get('volume_serial') and not data.get('issue_number'):
                    self.add_error('volume_serial', _("Volume or issue number mandatory"))

            #LILACS validation flag is mandatory when indexed in LILACS
            indexed_list = [indexed.acronym for indexed in self.cleaned_data.get('indexed_database')]
            if 'LILACS' in indexed_list:
                lilacs_validation_flag = self.cleaned_data.get('LILACS_indexed')
                if not lilacs_validation_flag:
                    self.add_error('LILACS_indexed', _("Required when indexed in LILACS database"))

        # Always return the full collection of cleaned data.
        return data

    def clean_LILACS_indexed(self):
        data = self.cleaned_data.get('LILACS_indexed')
        if data is True:
            self.is_LILACS = True

        return data

    def clean_corporate_author(self):
        field = 'corporate_author'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        resp_list = ['edt', 'com', 'coord', 'org']
        literature_type = self.document_type[0]

        if data and self.is_LILACS and status == 1:
            occ = 0
            for author in data:
                occ = occ + 1
                author_resp = author.get('_r')
                message_item = _("Author %s: ") % occ
                if author_resp and not author_resp in resp_list:
                    message = _("Degree of responsibility incompatible with LILACS")
                    message = string_concat(message_item, message)
                    self.add_error(field, message)

        return data

    def validate_author_field(self, field):
        data = self.cleaned_data.get(field)
        abbreviation_list = [' JR.', ' JR ', 'Fº', ' jr.', ' jr ', 'fº', ' Jr.', ' Jr ', ' jR.', ' jR ']
        resp_list = ['edt', 'com', 'coord', 'org']
        literature_type = self.document_type[0]
        type_of_journal = self.cleaned_data.get('type_of_journal', 'p')
        status = self.cleaned_data.get('status')

        # skip validation when record is deleted or refused
        if status == 2 or status == 3:
            return data

        if self.document_type[0] == 'T' and not 'a' in self.document_type:
            if not data:
                self.add_error(field, _("Mandatory"))
            else:
                occ = 0
                for author in data:
                    occ = occ + 1
                    author_name = author.get('text', '')
                    message_item = _("Author %s: ") % occ
                    if author_name == 'Anon':
                        message = _("Thesis's author anonymous")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)
                    if not ',' in author_name:
                        message = _("Comma abscent")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)
                    elif not ', ' in author_name:
                        message = _("Insert space after comma")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)
                    if author.get('_1') or author.get('_2') or author.get('_3') or author.get('_c') or author.get('_r'):
                        message = _("Affiliation information in Thesis/Dissertation must be provide at 'Institution to which it is submitted' field")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

        elif data:
            occ = 0
            for author in data:
                occ = occ + 1
                author_name = author.get('text', '')
                message_item = _("Author %s: ") % occ
                if author_name != 'Anon':
                    if not ',' in author_name and self.is_LILACS:
                        message = _("Comma absense or error in the word Anon")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)
                    else:
                        if ',' in author_name and not ', ' in author_name:
                            message = _("Insert space after comma")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)
                        if '.' in author_name and not '. ' in author_name:
                            message = _("Insert space after point")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)
                        if any(abbreviation.decode('utf-8') in author_name for abbreviation in abbreviation_list):
                            message = _("Invalid abbreviation input Junior and/or Filho")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)

                    if status == 1 and literature_type == 'S' and self.is_LILACS and type_of_journal == 'p' and not author.get('_1'):
                        message = _("Affiliation institution level 1 mandatory")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if status == 1 and not author.get('_p') and author.get('_1') and author.get('_1').lower() != 's.af':
                        message = _("Affiliation country mandatory")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if status == 1 and (not author.get('_1') or author.get('_1').lower() == 's.af'):
                        if author.get('_2') or author.get('_3') or author.get('_p') or author.get('_c'):
                            message = _("For absent or s.af affiliation do not describe the others affiliation atributes")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)

                    if status == 1 and self.is_LILACS and author.get('_r'):
                        if not author.get('_r') in resp_list:
                            message = _("Degree of responsibility incompatible with LILACS")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)

                    for key, value in author.iteritems():
                        if value.strip().endswith('.'):
                            message = _("Point at end of field is not allowed")
                            subfield = _(" at subfield %s ") % key[1:]
                            message = string_concat(message_item, message, subfield)
                            self.add_error(field, message)

        return data

    # field tag 10
    def clean_individual_author(self):
        data = self.validate_author_field('individual_author')

        return data

    # field tag 16
    def clean_individual_author_monographic(self):
        data = self.validate_author_field('individual_author_monographic')

        return data

    def clean_electronic_address(self):
        field = 'electronic_address'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']
        url_list = []

        if data and status == 1:
            occ = 0
            for electronic_address in data:
                occ = occ + 1
                url = electronic_address.get('_u', '')
                message_item = _("item %s: ") % occ
                if self.is_LILACS:
                    if electronic_address.get('_q', '') == '':
                        message = _("File extension attribute is mandatory")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if electronic_address.get('_y', '') == '':
                        message = _("File type attribute is mandatory")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if electronic_address.get('_i', '') not in LILACS_compatible_languages:
                        message = _("Language incompatible with LILACS")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if url not in url_list:
                        url_list.append(url)
                    else:
                        message = _("URL duplicated")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

        return data

    def clean_record_type(self):
        field = 'record_type'
        data = self.cleaned_data[field]
        status = self.cleaned_data.get('status')
        message = ''

        if status == 1:
            if self.is_visiblefield(field) and not data:
                self.add_error(field, _("Mandatory"))
            elif self.is_LILACS:
                if data == 'c':
                    message = _("Printed music in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'd':
                    message = _("Manuscript music in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'e':
                    message = _("Printed cartographic material in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'f':
                    message = _("Manuscript cartographic material in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'j':
                    message = _("Musical sound recording in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'k':
                    message = _("Two-dimensional nonprojectable graphic in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'm':
                    message = _("Computer file in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'o':
                    message = _("Kit in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'p':
                    message = _("Mixed material in the Record Type is incompatible with the LILACS Methodology")
                elif data == 'r':
                    message = _("Three-dimensional artifact or naturally occurring object in the Record Type is incompatible with the LILACS Methodology")
                elif data == 't':
                    message = _("Manuscript language material in the Record Type is incompatible with the LILACS Methodology")

                if message:
                    self.add_error(field, message)

        return data

    def clean_item_form(self):
        field = 'item_form'
        data = self.cleaned_data[field]
        electronic_address = self.cleaned_data.get('electronic_address')
        pages = self.cleaned_data.get('pages')
        pages_monographic = self.cleaned_data.get('pages_monographic')
        record_type = self.cleaned_data.get('record_type')
        status = self.cleaned_data.get('status')

        if data and self.is_LILACS and status == 1:
            if electronic_address:
                if not pages and not pages_monographic and not data == 's':
                    self.add_error(field, _("For the tradicional material of LILACS which is only in electronic form you should describe it as Electronic"))

            if record_type == 'a':
                if self.document_type[0] == 'S' and data != 's':
                    self.add_error(field, _('For articles, item form must be empty or Eletronic'))

        return data

    def clean_type_of_journal(self):
        field = 'type_of_journal'
        data = self.cleaned_data.get(field)
        record_type = self.cleaned_data.get('record_type')
        status = self.cleaned_data.get('status')

        if self.is_LILACS and record_type == 'a' and status == 1:
            if self.document_type[0] == 'S' and (data != 'p' and data != 'u'):
                self.add_error(field, _('For articles indexed in LILACS, type of journal must be Journal or Separatum'))

        return data

    def clean_title_serial(self):
        data = self.cleaned_data['title_serial']

        if self.document_type == 'S':
            title_serial = self.cleaned_data.get('title_serial')
            title_serial_other = self.data.get('title_serial_other')

            if title_serial_other and self.is_LILACS:
                self.add_error('title_serial', _("For LILACS references is mandatory select a journal from the list"))

            if title_serial and title_serial_other and not self.is_LILACS:
                self.add_error('title_serial', _("Please choose one journal from the list or use blank to inform other journal title"))

            if not title_serial_other and not title_serial:
                self.add_error('title_serial', _("Mandatory"))

            if title_serial_other and not self.is_LILACS:
                data = title_serial_other
            else:
                data = title_serial
        else:
            if self.is_visiblefield('title_serial') and not data:
                self.add_error('title_serial', _("Mandatory"))

        return data

    def clean_title(self):
        field = 'title'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']
        url_list = []

        if self.is_visiblefield('title'):
            if not data:
                self.add_error(field, _("Mandatory"))
            else:
                occ = 0
                for title in data:
                    occ = occ + 1
                    url = title.get('_u', '')
                    message_item = _("Title %s: ") % occ
                    if self.is_LILACS:
                        if title.get('_i', '') not in LILACS_compatible_languages:
                            message = _("Language incompatible with LILACS")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)
                    # check pontuation errors
                    self.check_all_pontuation(title.get('text'), field, message_item)

        return data

    def clean_title_monographic(self):
        field = 'title_monographic'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']

        if self.is_visiblefield('title_monographic'):
            if data:
                occ = 0
                for title in data:
                    occ = occ + 1
                    url = title.get('_u', '')
                    message_item = _("Title %s: ") % occ
                    if self.is_LILACS:
                        if title.get('_i', '') not in LILACS_compatible_languages:
                            message = _("Language incompatible with LILACS")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)
                    # check pontuation errors
                    self.check_all_pontuation(title.get('text'), field, message_item)
            else:
                self.add_error(field, _("Mandatory"))

        return data

    def clean_english_title_monographic(self):
        field = 'english_title_monographic'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')

        if self.is_visiblefield(field) and status == 1:
            self.check_all_pontuation(data, field)

            title = self.cleaned_data.get('title_monographic')
            if title:
                title_languages = [t.get('_i') for t in title]

            if not(data):
                if self.is_LILACS and title and not 'en' in title_languages:
                    self.add_error(field, _("Mandatory"))
            else:
                if self.is_LILACS and 'en' in title_languages:
                    self.add_error(field, _("Invalid fill. Don't translate title in English"))

        return data

    def clean_english_translated_title(self):
        field = 'english_translated_title'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        title_languages = []

        if self.is_visiblefield(field) and status == 1:
            title = self.cleaned_data.get('title')
            if title:
                title_languages = [t.get('_i') for t in title]

            if not(data):
                if self.is_LILACS and title and not 'en' in title_languages and status == 1:
                    self.add_error(field, _("Mandatory"))
            else:
                if self.is_LILACS and 'en' in title_languages:
                    self.add_error(field, _("Invalid fill. Don't translate title in English"))


        return data

    def clean_title_collection(self):
        field = 'title_collection'
        data = self.cleaned_data.get(field)
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']

        if self.is_visiblefield('title_collection'):
            if data:
                occ = 0
                for title in data:
                    occ = occ + 1
                    url = title.get('_u', '')
                    message_item = _("Title %s: ") % occ
                    if self.is_LILACS:
                        if title.get('_i', '') not in LILACS_compatible_languages:
                            message = _("Language incompatible with LILACS")
                            message = string_concat(message_item, message)
                            self.add_error(field, message)
                    # check pontuation errors
                    self.check_all_pontuation(title.get('text'), field, message_item)
            else:
                self.add_error(field, _("Mandatory"))

        return data


    def clean_publication_date(self):
        field = 'publication_date'
        data = self.cleaned_data[field]
        status = self.cleaned_data.get('status')

        if self.is_visiblefield(field) and (status == 1 or self.document_type == 'S'):
            search_year = re.search('[0-9]{4}', data)
            if search_year == None and data != 's.d' and data != 's.f':
                self.add_error(field, _("Date without year"))

            if not data:
                self.add_error(field, _("Mandatory"))

        return data


    def clean_publication_date_normalized(self):
        normalized_field = 'publication_date_normalized'
        normalized_date = self.cleaned_data[normalized_field]
        raw_date = self.cleaned_data.get('publication_date')
        status = self.cleaned_data.get('status')

        if self.is_visiblefield(normalized_field) and (status == 1 or self.document_type == 'S'):
            if raw_date != 's.d' and raw_date != 's.f':
                if not normalized_date:
                    self.add_error(normalized_field, _("Entering information in this field is conditional to filling out publication date field"))
                else:
                    if len(normalized_date) != 8:
                        self.add_error(normalized_field, _("Different of 8 characters"))

                    if self.is_LILACS and int(normalized_date[:4]) < 1982:
                        self.add_error(normalized_field, _("Incompatible with LILACS"))

                    # extract year from raw date field
                    search_year = re.search('([0-9]{4})', raw_date)
                    if search_year != None:
                        raw_date_year = search_year.group(1)

                        if not normalized_date[0:4] == raw_date_year:
                            error_message = _("Normalized date year must be '%s'") % raw_date_year
                            self.add_error(normalized_field, error_message)

                        if len(raw_date) == 4:
                            incomplete_normalized_date = "%s0000" % raw_date
                            if not normalized_date == incomplete_normalized_date:
                                error_message = _("Error in the date, use: %s") % incomplete_normalized_date
                                self.add_error(normalized_field, error_message)
            else:
                if normalized_date:
                    msg = _("Leave blank, publication date = %s") % raw_date
                    self.add_error(normalized_field, msg)

        return normalized_date

    def clean_pages(self):
        field = 'pages'
        data = self.cleaned_data[field]
        status = self.cleaned_data.get('status')

        if data and self.is_visiblefield(field) and status == 1:
            if len(data) > 4:
                self.add_error(field, _('Do not have more than 4 occurrences, use passim'))
            else:
                occ = 0
                for page in data:
                    occ = occ + 1
                    text = page.get('text', '')
                    first = page.get('_f', '')
                    last = page.get('_l', '')
                    elocation = page.get('_e', '')
                    message_item = _("item %s: ") % occ

                    if first == 'passim' and last != '':
                        message = _("If the attribute first is passim, the attribute last should be empty")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if first != '' and first != 'passim' and not last:
                        message = _("Attribute last is missing")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if last != '' and not first:
                        message = _("Attribute first is missing")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if text and (text[0] != '[' or text[-1] != ']'):
                        message = _("Square brackets are missing [ ]")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)

                    if elocation != '' and (first or last or text):
                        message = _("When the electronic location attribute is informed the others attributes should be empty")
                        message = string_concat(message_item, message)
                        self.add_error(field, message)


        return data

    def clean_thesis_dissertation_institution(self):
        field = 'thesis_dissertation_institution'
        data = self.cleaned_data[field]
        status = self.cleaned_data.get('status')

        if self.is_visiblefield(field) and status == 1 and not data:
            self.add_error(field, _('Mandatory'))

        return data

    def clean_thesis_dissertation_academic_title(self):
        field = 'thesis_dissertation_academic_title'
        data = self.cleaned_data[field]
        status = self.cleaned_data.get('status')

        if self.is_visiblefield(field) and status == 1:
            if not data:
                self.add_error(field, _('Mandatory'))
            else:
                if self.is_LILACS:
                    allowed_values = []
                    for controled_value in AuxCode.objects.filter(field=field):
                        allowed_values.extend(controled_value.get_all_labels())

                    if data not in allowed_values:
                        self.add_error(field, _('LILACS incompatible'))

        return data

    def clean_publication_city(self):
        field = 'publication_city'
        data = self.cleaned_data[field]

        if self.is_visiblefield(field) and self.cleaned_data['status'] == 1:
            if not(data):
                self.add_error(field, _('Mandatory'))

        return data

    def clean_publication_country(self):
        field = 'publication_country'
        data = self.cleaned_data[field]

        if self.is_visiblefield(field) and self.cleaned_data['status'] == 1:
            if not(data):
                if self.cleaned_data['publication_city'] != 's.l':
                    self.add_error(field, _('Entering information in this field is conditional to filling out publication city field'))
            else:
                if self.is_LILACS:
                    country_list_latin_caribbean = [c for c in Country.objects.filter(LA_Caribbean=True)]
                    if data not in country_list_latin_caribbean:
                        self.add_error(field, _('LILACS incompatible'))

        return data

    def clean_issn(self):
        field = 'issn'
        data = self.cleaned_data[field]

        if data and self.is_visiblefield(field):
            if len(data) > 9:
                self.add_error(field, _('Maximum number of characteres = 9'))

        return data

    def clean_text_language(self):
        field = 'text_language'
        data = self.cleaned_data.get(field)
        status = self.cleaned_data.get('status')
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']

        if self.is_visiblefield(field) and status == 1:
            if not data:
                self.add_error(field, _('Mandatory'))
            else:
                if self.is_LILACS:
                    for text_language in data:
                        if text_language not in LILACS_compatible_languages:
                            self.add_error(field, _('Language incompatible with LILACS'))

        return data

    def clean_publisher(self):
        field = 'publisher'
        data = self.cleaned_data[field]

        if self.is_visiblefield(field) and self.cleaned_data['status'] == 1:
            if not data:
                self.add_error(field, _('Mandatory'))

        return data

    def clean_indexed_database(self):
        field = 'indexed_database'
        data = self.cleaned_data[field]

        if self.is_visiblefield(field) and self.cleaned_data['status'] == 1:
            if not data:
                self.add_error(field, _('Mandatory'))

        return data

    def clean_doi_number(self):
        field = 'doi_number'
        data = self.cleaned_data.get(field)

        if data and self.is_visiblefield(field) and self.cleaned_data['status'] == 1:
            if not data[0].isdigit():
                self.add_error(field, _('Please inform a valid DOI number. Ex. 10.1000/xyz123'))

        return data


    def save(self, *args, **kwargs):
        obj = super(BiblioRefForm, self).save(commit=False)

        # if is a new analytic save reference source info
        if self.reference_source:
            obj.source = self.reference_source

        # treatment for MS / TS record types
        if self.document_type.startswith('MS') or self.document_type.startswith('TS'):
            obj.literature_type = self.document_type[0:2]
            obj.treatment_level = self.document_type[2:]
        else:
            obj.literature_type = self.document_type[0]
            obj.treatment_level = self.document_type[1:]

        if self.document_type[0] == 'S':
            if self.document_type == 'S':
                obj.reference_title = u"{0}; {1} ({2}), {3}".format(self.cleaned_data['title_serial'],
                                                                    self.cleaned_data['volume_serial'],
                                                                    self.cleaned_data['issue_number'],
                                                                    self.cleaned_data['publication_date_normalized'][:4])
            elif self.document_type == 'Sas':
                if self.cleaned_data['title']:
                    analytic_title = self.cleaned_data['title']
                    analytic_title = analytic_title[0]['text']
                    obj.reference_title = u"{0} | {1}".format(obj.source.reference_title, analytic_title)
        else:
            if 'a' in self.document_type:
                analytic_title = self.cleaned_data['title']
                analytic_title = analytic_title[0]['text']
                obj.reference_title = u"{0} | {1}".format(obj.source.reference_title, analytic_title)
            else:
                if self.document_type == 'Mc':
                    ref_title = self.cleaned_data['title_collection'][0]['text']
                else:
                    ref_title = self.cleaned_data['title_monographic'][0]['text']

                obj.reference_title = u"{0}".format(ref_title)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # fix values for specific fields for llxp editor profile
        if self.user_role == 'editor_llxp':
            if self.document_type == 'Sas':
                obj.record_type = 'a'       # textual material
                obj.item_form = 's'         # eletronic
                obj.type_of_journal = 'p'   # periodical
            # mark source of serial with LLXP status
            elif self.document_type == 'S':
                obj.status = '0'

        # add default value for publisher field in thesis record
        if self.document_type == 'Tm':
            obj.publisher = 's.n'

        # check if reference doesn't have indexer_cc_code info
        if not obj.indexer_cc_code:
            ctype = obj.get_content_type_id()
            # check if user has indexed this document
            has_indexed = Descriptor.objects.filter(object_id=obj.id, content_type_id=ctype,
                                                    created_by=self.user).exists()

            if has_indexed:
                # update reference indexer_cc_code field
                obj.indexer_cc_code = self.user_data.get('user_cc','')

        # save object
        obj.save()

        return obj

class BiblioRefSourceForm(BiblioRefForm):
    class Meta:
        model = ReferenceSource
        exclude = ('cooperative_center_code', 'indexer_cc_code')


class BiblioRefAnalyticForm(BiblioRefForm):
    class Meta:
        model = ReferenceAnalytic
        exclude = ('source', 'cooperative_center_code', 'indexer_cc_code')


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput)


class LibraryForm(forms.ModelForm):
    class Meta:
        model = ReferenceLocal
        exclude = ('cooperative_center_code',)


class ComplementForm(forms.ModelForm):
    class Meta:
        model = ReferenceComplement
        exclude = ('source',)

    def clean(self):
        data = self.cleaned_data

        if not data.get('conference_name') and (data.get('conference_sponsoring_institution') or
           data.get('conference_date') or data.get('conference_normalized_date') or
           data.get('conference_city') or data.get('conference_country')):
                self.add_error('conference_name', _("Event name mandatory"))

        if (not data.get('project_name') and not data.get('project_number')) and data.get('project_sponsoring_institution'):
            self.add_error('project_name', _("Project name OR Project number mandatory"))

        return data

    def clean_conference_date(self):
        field = 'conference_date'
        conference = self.cleaned_data.get('conference_name', '')
        data = self.cleaned_data.get(field)

        if conference and not data:
            self.add_error(field, _("Mandatory"))

        return data

    def clean_conference_normalized_date(self):
        conference = self.cleaned_data.get('conference_name', '')
        normalized_field = 'conference_normalized_date'
        normalized_date = self.cleaned_data[normalized_field]
        raw_date = self.cleaned_data.get('conference_date')

        if conference:
            if raw_date != 's.d' and raw_date != 's.f':
                if not normalized_date:
                    self.add_error(normalized_field, _("Mandatory"))
                else:
                    if len(normalized_date) != 8:
                        self.add_error(normalized_field, _("Different of 8 characters"))

                    if len(raw_date) == 4:
                        if not normalized_date == "%s0000" % raw_date:
                            self.add_error(normalized_field, _("Error in the date"))
            else:
                if normalized_date:
                    msg = _("Leave blank, publication date = %s") % raw_date
                    self.add_error(normalized_field, msg)

        return normalized_date

    def clean_conference_city(self):
        field = 'conference_city'
        conference = self.cleaned_data.get('conference_name', '')
        data = self.cleaned_data.get(field)

        if conference and not data:
            self.add_error(field, _("Mandatory"))

        return data


class DescriptorForm(forms.ModelForm):
    def save(self, *args, **kwargs):
        obj = super(DescriptorForm, self).save(commit=False)
        # for bibliographic default value for descriptor is admited
        obj.status = 1
        obj.save()

# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(
    Descriptor,
    form=DescriptorForm,
    formset=BaseDescriptorInlineFormSet,
    exclude=('status',),
    can_delete=True,
    extra=1
)

AttachmentFormSet = generic_inlineformset_factory(Attachment, form=AttachmentForm,
                                                  exclude=('short_url',), can_delete=True, extra=1)

LibraryFormSet = inlineformset_factory(Reference, ReferenceLocal, form=LibraryForm, extra=1,
                                       max_num=1, can_delete=False)

ComplementFormSet = inlineformset_factory(Reference, ReferenceComplement, form=ComplementForm, extra=1,
                                          max_num=1, can_delete=False)
