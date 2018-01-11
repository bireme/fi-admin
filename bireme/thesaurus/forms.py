# -*- coding: utf-8 -*-


from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings

from django import forms

from thesaurus.models_thesaurus import Thesaurus
from thesaurus.models_qualifiers import *
from thesaurus.models_descriptors import *


# from django.forms.formsets import formset_factory


from django.utils.translation import ugettext_lazy as _


class ThesaurusForm(forms.ModelForm):
	class Meta:
		model = Thesaurus
		# fields = '__all__'
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

class TermListQualifForm(forms.ModelForm):
    class Meta:
        model = TermListQualif
        fields = '__all__'

# Descriptor ------------------------------------------------------------------
class IdentifierDescForm(forms.ModelForm):
    class Meta:
        model = IdentifierDesc
        # exclude = ()
        fields = '__all__'

    # date_created = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), required=False,
    #                              input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"))

    # date_revised = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), required=False,
    #                              input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date revised"))

    # date_established = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), required=False,
    #                              input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date established"))


class DescriptionDescForm(forms.ModelForm):
    class Meta:
        model = DescriptionDesc
        exclude = ()

class TreeNumbersListDescForm(forms.ModelForm):
    class Meta:
        model = TreeNumbersListDesc
        exclude = ()

class PreviousIndexingListDescForm(forms.ModelForm):
    class Meta:
        model = PreviousIndexingListDesc
        exclude = ()

# class ConceptListDescFormForm(forms.ModelForm):
#     class Meta:
#         model = ConceptListDescForm
#         exclude = ()

class TermListDescForm(forms.ModelForm):
    class Meta:
        model = TermListDesc
        exclude = ()




# FormSets
# Descriptor ------------------------------------------------------------------
DescriptionDescFormSet = inlineformset_factory(
    IdentifierDesc,
    DescriptionDesc,
    form=DescriptionDescForm,
    fields='__all__',
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
    extra=1
    )

# ConceptListDescFormSet = inlineformset_factory(
    # IdentifierDesc,
    # ConceptListDesc,
    # form=ConceptListDescForm,
    # fields='__all__',
    # extra=1
    # )

TermListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    TermListDesc,
    form=TermListDescForm,
    fields='__all__',
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

TermListQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    TermListQualif,
    form=TermListQualifForm,
    fields='__all__',
    extra=1
    )
