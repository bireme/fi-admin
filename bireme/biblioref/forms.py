#! coding: utf-8
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.forms import widgets
from django import forms
from form_utils.forms import BetterModelForm, FieldsetCollection
from form_utils.widgets import AutoResizeTextarea
from django.conf import settings

from main.models import Descriptor, Keyword, ResourceThematic
from utils.forms import DescriptorRequired, ResourceThematicRequired

from models import *
import simplejson


class SelectDocumentTypeForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = (
        # ('MS', _('Monograph Series')),
        # ('', _('Monograph in a Collection')),
        ('M', _('Monograph')),
        # ('N', _('Non conventional')),
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

        fieldsets = kwargs.pop('fieldsets', None)

        super(BiblioRefForm, self).__init__(*args, **kwargs)

        # used for fieldsets method for construct internal fieldset_collection
        self._fieldsets = fieldsets

        # hidden status field for documentalist profile
        if self.user_data['service_role'].get('BiblioRef') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()

    def fieldsets(self):
        if not self._fieldset_collection:
            self._fieldset_collection = FieldsetCollection(self, self._fieldsets)

        return self._fieldset_collection

    def save(self, *args, **kwargs):
        obj = super(BiblioRefForm, self).save(commit=False)

        # if is a new analytic save reference source info
        if self.reference_source:
            obj.source = self.reference_source

        obj.literature_type = self.document_type[0]
        obj.treatment_level = self.document_type[1:]

        print self.document_type

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

        elif self.document_type[0] == 'M':
            if self.document_type == 'M':
                obj.reference_title = u"{0} {1}".format(self.cleaned_data['title_monographic'],
                                                        self.cleaned_data['volume_monographic'])

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # save modifications
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


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(Descriptor, can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, can_delete=True, extra=1)
