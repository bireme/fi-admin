from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *

import simplejson

GENERIC_FIELDS = ()

class ResourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(ResourceForm, self).__init__(*args, **kwargs)

        if self.user_data['user_role'] == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()
            '''
            if not self.user_data['is_owner']:
                for field in self.fields:
                    self.fields[field].widget = widgets.HiddenInput()
            '''


    def save(self, *args, **kwargs):
        obj = super(ResourceForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for prevent POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # add cooperative center code to model for new records
        if self.user:
            if not obj.cooperative_center_code:
                user_cc = settings.DEFAULT_COOPERATIVE_CENTER
                if not self.user.is_superuser:
                    user_data = simplejson.loads(self.user.profile.data)
                    user_cc = user_data['cc']

                obj.cooperative_center_code = user_cc

        # save modifications
        obj.save()

        return obj

    class Meta:
        model  =Resource
        exclude = ('cooperative_center_code',)

        source_language = forms.MultipleChoiceField()

        source_type = forms.MultipleChoiceField()


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


#def formfield_callback(field):
#     self.fields[key].required = False
#    if isinstance(field, models.ChoiceField) and field.name == 'target_field_name':
#        return fields.ChoiceField(choices = SAMPLE_CHOICES_LIST, label='Sample Label')
#    return field.formfield()


# definition of inline formsets

DescriptorFormSet = inlineformset_factory(Resource, Descriptor, can_delete=True, extra=1)

DescriptorFormSetForDoc = inlineformset_factory(Resource, Descriptor, can_delete=True, extra=1, exclude=('status'))


ResourceThematicFormSet = inlineformset_factory(Resource, ResourceThematic, can_delete=True, extra=1)

ResourceThematicFormSetForDoc = inlineformset_factory(Resource, ResourceThematic, can_delete=True, extra=1, exclude=('status'))


ThematicAreaTranslationFormSet = inlineformset_factory(ThematicArea, ThematicAreaLocal, form=ThematicAreaLocalForm, can_delete=True, extra=1)

LanguageTranslationFormSet = inlineformset_factory(SourceLanguage, SourceLanguageLocal, can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(SourceType, SourceTypeLocal, can_delete=True, extra=1)