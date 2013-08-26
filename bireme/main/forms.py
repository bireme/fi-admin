from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *

import simplejson

GENERIC_FIELDS = ('created', 'updated', 'creator', 'updater',)

class ResourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)

        return super(ResourceForm, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        obj = super(ResourceForm, self).save(commit=False)
        # add cooperative center code to model
        if self.user:
            if not obj.cooperative_center:
                user_cc = settings.DEFAULT_COOPERATIVE_CENTER
                if not self.user.is_superuser:
                    user_data = simplejson.loads(self.user.profile.data)
                    user_cc = user_data['cc']

                obj.cooperative_center = user_cc
        obj.save()
        return obj

    class Meta:
        model = Resource
        exclude = GENERIC_FIELDS + ('cooperative_center',)


class DescriptorForm(forms.ModelForm):
    class Meta:
        model = Descriptor
        exclude = GENERIC_FIELDS


class ThematicAreaForm(forms.ModelForm):

    class Meta:
        model = ThematicArea
        exclude = GENERIC_FIELDS

class ThematicAreaLocalForm(forms.ModelForm):

    class Meta:
        model = ThematicAreaLocal


class LanguageForm(forms.ModelForm):

    class Meta:
        model = SourceLanguage
        exclude = GENERIC_FIELDS

class LanguageLocalForm(forms.ModelForm):

    class Meta:
        model = SourceLanguageLocal


class TypeForm(forms.ModelForm):

    class Meta:
        model = SourceType
        exclude = GENERIC_FIELDS


class TypeLocalForm(forms.ModelForm):

    class Meta:
        model = SourceTypeLocal


DescriptorFormSet = inlineformset_factory(Resource, Descriptor, can_delete=True, extra=1)

ThematicAreaTranslationFormSet = inlineformset_factory(ThematicArea, ThematicAreaLocal, form=ThematicAreaLocalForm, can_delete=True, extra=1)

LanguageTranslationFormSet = inlineformset_factory(SourceLanguage, SourceLanguageLocal, can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(SourceType, SourceTypeLocal, can_delete=True, extra=1)