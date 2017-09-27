from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.forms.formsets import formset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *
from main.models import Descriptor, Keyword

from utils.forms import DescriptorRequired

import simplejson
import time


class TitleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(TitleForm, self).__init__(*args, **kwargs)

        if self.user_data['service_role'].get('Title') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()

    def clean_initial_date(self):
        field = 'initial_date'
        data = self.cleaned_data[field]
        status = self.cleaned_data['status'] if 'status' in self.cleaned_data else None
        message = ''

        if status and 'C' in status:
            if not data:
                message = _("The initial date field is mandatory when publish status field value is 'current'")

        if message:
            self.add_error(field, message)

        return data

    def clean_final_date(self):
        field = 'final_date'
        data = self.cleaned_data[field]
        status = self.cleaned_data['status'] if 'status' in self.cleaned_data else None
        message = ''

        if status and 'D' in status:
            if not data:
                message = _("The final date field is mandatory when publish status field value is 'suspended or closed'")

        if message:
            self.add_error(field, message)

        return data

    def clean_state(self):
        field = 'state'
        data = self.cleaned_data[field]
        country = self.cleaned_data['country'] if 'country' in self.cleaned_data else None
        c_list = [c.code for c in country] if country else None
        message = ''

        if c_list and 'BR' in c_list:
            if not data:
                message = _("The state field is mandatory when country field value is 'Brazil'")

        if message:
            self.add_error(field, message)

        return data

    def save(self, *args, **kwargs):
        obj = super(TitleForm, self).save(commit=False)

        # save modifications
        if not obj.id_number:
            data = Title.objects.latest('id')

            if not data:
                id = 1
            else:
                id = int(data.id_number) + 1

            obj.id_number = id

        obj.last_change_date = time.strftime('%Y%m%d')

        obj.save()

        return obj

    class Meta:
        model = Title
        exclude = ( 'id_number', 'record_type', 'treatment_level', 'cooperative_center_code', 'last_change_date', )


class OnlineResourcesForm(forms.ModelForm):
    def save(self, *args, **kwargs):
        obj = super(OnlineResourcesForm, self).save(commit=False)

        # save modifications
        if not obj.creation_date:
            obj.creation_date = time.strftime('%Y%m%d')

        obj.save()

        return obj

    class Meta:
        model = OnlineResources
        exclude = ( 'creation_date', 'tco', 'ndb', 'pca', 'access_control', )


class TitleVarianceForm(forms.ModelForm):
    def clean(self):
        field = 'type'
        data = self.cleaned_data
        type = data.get(field)
        label = data.get('label') if 'label' in data else None
        issn = data.get('issn') if 'issn' in data else None
        initial_year = data.get('initial_year') if 'initial_year' in data else None
        initial_volume = data.get('initial_volume') if 'initial_volume' in data else None
        initial_number = data.get('initial_number') if 'initial_number' in data else None
        message = ''

        if label or issn:
            if not type:
                message = _("The type field is mandatory when title, ISSN, initial year, initial volume or initial number fields value are not empty")

        if message:
            self.add_error(field, message)

        return data


class AuditForm(forms.ModelForm):
    def clean(self):
        field = 'type'
        data = self.cleaned_data
        type = data.get(field)
        label = data.get('label') if 'label' in data else None
        issn = data.get('issn') if 'issn' in data else None
        message = ''

        if label or issn:
            if not type:
                message = _("The type field is mandatory when title or ISSN fields value are not empty")

        if message:
            self.add_error(field, message)

        return data


# Definition of inline formsets

DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=DescriptorRequired, can_delete=True, extra=1, exclude=('primary', ))
KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)
OnlineResourcesFormSet = inlineformset_factory(Title, OnlineResources, form=OnlineResourcesForm, can_delete=True, extra=1)
AuditFormSet = inlineformset_factory(Title, Audit, form=AuditForm, fields = '__all__', can_delete=True, extra=1)
TitleVarianceFormSet = inlineformset_factory(Title, TitleVariance, form=TitleVarianceForm, fields='__all__', can_delete=True, extra=1)
BVSSpecialtyFormSet = inlineformset_factory(Title, BVSSpecialty, fields='__all__', can_delete=True, extra=1)
IndexRangeFormSet = inlineformset_factory(Title, IndexRange, fields='__all__', can_delete=True, extra=1)
