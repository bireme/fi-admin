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

from main.models import Descriptor, ResourceThematic
from utils.forms import DescriptorRequired, ResourceThematicRequired
from title.models import Title
from attachments.models import Attachment

from models import *
import json


class SelectDocumentTypeForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = (
        # ('MS', _('Monograph Series')),
        # ('', _('Monograph in a Collection')),
        ('M', _('Monograph')),
        ('N', _('Non conventional')),
        ('S', _('Periodical Series')),
        # ('', _('Collection')),
        # ('TS', _('Thesis, Dissertation appearing as a Monograph Series')),
        ('T', _('Thesis, Dissertation')),
    )

    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)


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
            # source
            if self.document_type == 'S':
                self.fields['issn'].widget = widgets.HiddenInput()
            # analytic
            else:
                self.fields['record_type'].widget = widgets.HiddenInput()
                self.fields['item_form'].widget = widgets.HiddenInput()
                self.fields['type_of_journal'].widget = widgets.HiddenInput()
                self.fields['english_translated_title'].widget = widgets.HiddenInput()

        # hide LILACS_indexed field for llxp editor profile
        if self.user_role == 'editor_llxp':
            self.fields['LILACS_indexed'].widget = widgets.HiddenInput()

        # hide BIREME reviewed field for non BIREME users
        if self.user_data['user_cc'] != 'BR1.1':
            self.fields['BIREME_reviewed'].widget = widgets.HiddenInput()

        # load serial titles for serial analytic
        if self.document_type == 'S' and not self.reference_source:
            title_objects = Title.objects.all()

            # populate choice title list based on user profile
            if self.user_role == 'editor_llxp':
                # for LILACS Express editor return only serials with same editor_cc_code of current user
                title_list = [(t.shortened_title, t.shortened_title) for t in title_objects.filter(editor_cc_code = self.user_data['user_cc']).order_by('shortened_title')]
            else:
                # for regular users return a title list splited in two parts:
                # first journals that is indexed by user center code
                # last the titles that have indexer_cc_code filled
                title_list = [('', '')]
                title_list_indexer_code = [(t.shortened_title, t.shortened_title) for t in title_objects.filter(indexer_cc_code = self.user_data['user_cc']).order_by('shortened_title')]
                title_list_other = [(t.shortened_title, t.shortened_title) for t in title_objects.exclude(indexer_cc_code=u'').exclude(indexer_cc_code = self.user_data['user_cc']).order_by('shortened_title')]

                separator = "-----------"
                label_indexed = separator + __('Indexed by your cooperative center') + separator
                label_not_indexed = separator + __('Indexed by other cooperative centers') + separator

                if title_list_indexer_code:
                    title_list.extend([('', label_indexed)])
                    title_list.extend(title_list_indexer_code)
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


    def fieldsets(self):
        if not self._fieldset_collection:
            self._fieldset_collection = FieldsetCollection(self, self._fieldsets)

        return self._fieldset_collection

    def clean(self):
        data = self.cleaned_data
        error_messages = []

        for field_name, field_value in self.fields.iteritems():
            field_check = data.get(field_name)

            if isinstance(self.fields[field_name].widget, forms.widgets.Textarea):
                if '%' in field_check:
                    self.add_error(field_name, _("The % simbol don't separete occurences"))

            if isinstance(field_check, basestring):
                if field_check.strip().endswith('.'):

                    self.add_error(field_name, _("Point at end of field is not allowed"))
        # Always return the full collection of cleaned data.
        return data


    def clean_LILACS_indexed(self):
        data = self.cleaned_data['LILACS_indexed']
        if data is True:
            self.is_LILACS = True

        return data

    def validate_author_field(self, field):
        data = self.cleaned_data[field]
        abbreviation_list = [' JR.', ' JR ', 'Fº', ' jr.', ' jr ', 'fº', ' Jr.', ' Jr ', ' jR.', ' jR ']
        literature_type = self.document_type[0]
        type_of_journal = self.cleaned_data.get('type_of_journal', 'p')

        if self.document_type[0] == 'T':
            if not data:
                self.add_error(field, _("Mandatory"))
            else:
                occ = 0
                for author in data:
                    occ = occ + 1
                    author_name = author.get('text', '')
                    message_item = _("item %s: ") % occ
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
        elif data:
            occ = 0
            for author in data:
                occ = occ + 1
                author_name = author.get('text', '')
                message_item = _("item %s: ") % occ
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

                    if literature_type == 'S' and self.is_LILACS and type_of_journal == 'p' and not '_1' in author:
                        message = _("Subfield 1 affiliation mandatory")
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
        data = self.cleaned_data[field]
        LILACS_compatible_languages = ['pt', 'es', 'en', 'fr']
        url_list = []

        if data:
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
        message = ''

        if data and self.is_LILACS:
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


    def clean_title_serial(self):
        title_serial_other = self.data.get('title_serial_other')
        title_serial = self.cleaned_data['title_serial']

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

        return data

    def save(self, *args, **kwargs):
        new_reference = True

        obj = super(BiblioRefForm, self).save(commit=False)

        # if is a new analytic save reference source info
        if self.reference_source:
            obj.source = self.reference_source

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
                obj.reference_title = u"{0}".format(self.cleaned_data['title_monographic'])

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # fix values for specific fields for llxp editor profile
        if self.document_type == 'Sas' and self.user_role == 'editor_llxp':
            obj.record_type = 'a'       # textual material
            obj.item_form = 's'         # eletronic
            obj.type_of_journal = 'p'   # periodical

        # save object
        obj.save()

        return obj

class BiblioRefSourceForm(BiblioRefForm):
    class Meta:
        model = ReferenceSource
        exclude = ('cooperative_center_code',)


class BiblioRefAnalyticForm(BiblioRefForm):
    class Meta:
        model = ReferenceAnalytic
        exclude = ('source', 'cooperative_center_code',)


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput)

class LibraryForm(forms.ModelForm):
    class Meta:
        model = ReferenceLocal
        exclude = ('cooperative_center_code',)


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(Descriptor, can_delete=True, extra=1)
ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, can_delete=True, extra=1)
AttachmentFormSet = generic_inlineformset_factory(Attachment, form=AttachmentForm,
                                                  exclude=('short_url',), can_delete=True, extra=1)
LibraryFormSet = inlineformset_factory(Reference, ReferenceLocal, form=LibraryForm, extra=1,
                                       max_num=1, can_delete=False)
