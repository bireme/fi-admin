#! coding: utf-8
from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.forms import widgets
from django import forms
from django.conf import settings

from main.models import Descriptor, Keyword, ResourceThematic
from utils.forms import DescriptorRequired, ResourceThematicRequired

from models import *

class SelectDocumentTypeForm(forms.Form):
    DOCUMENT_TYPE_CHOICES = (
        ('1', _('Monograph Series')),
        ('2', _('Monograph in a Collection')),
        ('3', _('Monograph')),
        ('4', _('Non conventional')),
        ('5', _('Periodical Series')),
        ('6', _('Collection')),
        ('7', _('Thesis, Dissertation appearing as a Monograph Series')),
        ('8', _('Thesis, Dissertation')),
    )

    document_type = forms.ChoiceField(choices=DOCUMENT_TYPE_CHOICES)


class BiblioRefForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)
        self.field_list = kwargs.pop('field_list', None)

        super(BiblioRefForm, self).__init__(*args, **kwargs)

        # only display fields of the model listed at field_list parameter (filter by document_type at view)
        if self.field_list:
            # status fields must be always present at form
            self.field_list.insert(0, 'status')

            # remove fields of the model that is not in field_list
            for field_name in self.fields:
                if not field_name in self.field_list:
                    del self.fields[field_name]

            # change the default order of the fields to match the order in field_list
            fields_ordered = OrderedDict()
            for field_name in self.field_list:
                fields_ordered[field_name] = self.fields[field_name]

            self.fields = fields_ordered

        # hidden status field for documentalist profile
        if self.user_data['service_role'].get('BiblioRef') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()


    def save(self, *args, **kwargs):
        obj = super(BiblioRefForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # save modifications
        obj.save()

        return obj

    class Meta:
        model = Reference
        exclude = ('cooperative_center_code',)

        source_language = forms.MultipleChoiceField()


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=DescriptorRequired, 
                                                  can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, 
                                                        formset=ResourceThematicRequired, can_delete=True, extra=1)

