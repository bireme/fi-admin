# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory


from thesaurus.models_thesaurus import Thesaurus
from thesaurus.models_qualifiers import *
from thesaurus.models_descriptors import *


from django.utils.translation import ugettext_lazy as _

from django.forms import widgets
from django import forms
from form_utils.forms import BetterModelForm, FieldsetCollection
from django.conf import settings



class ThesaurusForm(forms.ModelForm):
    class Meta:
        model = Thesaurus
        exclude = ()

# Qualifier -------------------------------------------------------------------
class IdentifierQualifForm(forms.ModelForm):
    class Meta:
        model = IdentifierQualif
        fields = '__all__'

class DescriptionQualifForm(forms.ModelForm):
    class Meta:
        model = DescriptionQualif
        fields = '__all__'

class TreeNumbersListQualifForm(forms.ModelForm):
    class Meta:
        model = TreeNumbersListQualif
        fields = '__all__'

class ConceptListQualifForm(forms.ModelForm):
    class Meta:
        model = ConceptListQualif
        fields = '__all__'

class TermListQualifForm(forms.ModelForm):
    class Meta:
        model = TermListQualif
        fields = '__all__'

# Descriptor ------------------------------------------------------------------
class IdentifierDescForm(forms.ModelForm):
    class Meta:
        model = IdentifierDesc
        fields = '__all__'

    def clean_decs_code(self):
        data = self.cleaned_data.get('decs_code')
        if not data:
            message = _("Campo obrigatorio - teste decs_code")
            self.add_error('decs_code',message)

        return data


class DescriptionDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

    # def clean(self):
    #     field = 'descriptor_name'
    #     data = self.cleaned_data
    #     descriptor_name = data.get(field)

    #     if not descriptor_name:
    #         message = _("Campo obrigatorio - teste descriptor_name")
    #         self.add_error(field,message)

    #     return data


class TreeNumbersListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

class PreviousIndexingListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'


class ConceptListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

# class ConceptRelationDescForm(forms.ModelForm):
#     class Meta:
#         model = ConceptRelationDesc
#         fields = '__all__'

class TermListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'



# FormSets
# Descriptor ------------------------------------------------------------------
DescriptionDescFormSet = inlineformset_factory(
    IdentifierDesc,
    DescriptionDesc,
    form=DescriptionDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

TreeNumbersListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    TreeNumbersListDesc,
    form=TreeNumbersListDescForm,
    fields='__all__',
    extra=1
    )

PreviousIndexingListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    PreviousIndexingListDesc,
    form=PreviousIndexingListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

ConceptListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    ConceptListDesc,
    form=ConceptListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

# ConceptRelationDescFormSet = inlineformset_factory(
#     IdentifierDesc,
#     ConceptRelationDesc,
#     form=ConceptRelationDescForm,
#     fields='__all__',
#     can_delete=True,
#     extra=1
#     )

TermListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    TermListDesc,
    form=TermListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

# Qualifiers ------------------------------------------------------------------
DescriptionQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    DescriptionQualif,
    form=DescriptionQualifForm,
    fields='__all__',
    extra=1
    )

TreeNumbersListQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    TreeNumbersListQualif,
    form=TreeNumbersListQualifForm,
    fields='__all__',
    extra=1
    )


ConceptListQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    ConceptListQualif,
    form=ConceptListQualifForm,
    fields='__all__',
    extra=1
    )


TermListQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    TermListQualif,
    form=TermListQualifForm,
    fields='__all__',
    extra=1
    )

