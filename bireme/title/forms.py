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

    def save(self, *args, **kwargs):
        obj = super(TitleForm, self).save(commit=False)

        # save modifications
        obj.last_change_date = time.strftime('%Y%m%d')
        obj.save()

        return obj

    class Meta:
        model  = Title
        exclude = ('record_type', 'treatment_level', 'cooperative_center_code', 'last_change_date', )


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
        exclude = ('creation_date', )


# definition of inline formsets

DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=DescriptorRequired, can_delete=True, extra=1)
KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)
OnlineResourcesFormSet = inlineformset_factory(Title, OnlineResources, form=OnlineResourcesForm, can_delete=True, extra=1)
BVSSpecialtyFormSet = inlineformset_factory(Title, BVSSpecialty, can_delete=True, extra=1)
TitleVarianceFormSet = inlineformset_factory(Title, TitleVariance, can_delete=True, extra=1)
IndexRangeFormSet = inlineformset_factory(Title, IndexRange, can_delete=True, extra=1)
AuditFormSet = inlineformset_factory(Title, Audit, can_delete=True, extra=1)
