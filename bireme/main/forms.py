from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory, BaseGenericInlineFormSet

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *

from utils.forms import DescriptorRequired, ResourceThematicRequired

import simplejson

GENERIC_FIELDS = ()

class ResourceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(ResourceForm, self).__init__(*args, **kwargs)

        if self.user_data['service_role'].get('LIS') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()


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
        model = Resource
        exclude = ('cooperative_center_code', )

        source_language = forms.MultipleChoiceField()
        source_type = forms.MultipleChoiceField()


class ThematicAreaForm(forms.ModelForm):

    class Meta:
        model = ThematicArea
        exclude = GENERIC_FIELDS

class ThematicAreaLocalForm(forms.ModelForm):

    class Meta:
        model = ThematicAreaLocal
        fields = '__all__'


class LanguageForm(forms.ModelForm):

    class Meta:
        model = SourceLanguage
        exclude = GENERIC_FIELDS

class LanguageLocalForm(forms.ModelForm):

    class Meta:
        model = SourceLanguageLocal
        fields = '__all__'


class TypeForm(forms.ModelForm):

    class Meta:
        model = SourceType
        exclude = GENERIC_FIELDS


class TypeLocalForm(forms.ModelForm):

    class Meta:
        model = SourceTypeLocal
        fields = '__all__'


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=DescriptorRequired, exclude=['primary'],
                                                  can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)
ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, formset=ResourceThematicRequired,
                                                        can_delete=True, extra=1)

ThematicAreaTranslationFormSet = inlineformset_factory(ThematicArea, ThematicAreaLocal,
                                                       form=ThematicAreaLocalForm, can_delete=True, extra=1)

LanguageTranslationFormSet = inlineformset_factory(SourceLanguage, SourceLanguageLocal,
                                                   fields='__all__', can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(SourceType, SourceTypeLocal, fields='__all__',
                                               can_delete=True, extra=1)
