from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *


GENERIC_FIELDS = ('created', 'updated', 'creator', 'updater',)

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        exclude = GENERIC_FIELDS


class DescriptorForm(forms.ModelForm):
    class Meta:
        model = Descriptor
        exclude = GENERIC_FIELDS


DescriptorFormSet = inlineformset_factory(Resource, Descriptor, can_delete=True, extra=1)