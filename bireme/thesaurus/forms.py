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

from django.conf import settings

from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS

import requests

class ThesaurusForm(forms.ModelForm):
    class Meta:
        model = Thesaurus
        exclude = ()

# Qualifier -------------------------------------------------------------------
# Register - Form1
class IdentifierQualifForm(forms.ModelForm):
    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_revised = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date revised"), required=False)
    date_established = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date established"), required=False)

    class Meta:
        model = IdentifierQualif
        fields = '__all__'

    # Verifica a quantidade de caracteres e formatacao adequada
    def clean_abbreviation(self):
        data = self.cleaned_data.get('abbreviation')
        # print 'abbreviation---',data
        # Força que seja maiusculo
        upper_data = data.upper()
        # print 'M -->',upper_data
        data = upper_data
        return data



class DescriptionQualifForm(forms.ModelForm):
    class Meta:
        model = DescriptionQualif
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }

class TreeNumbersListQualifForm(forms.ModelForm):
    class Meta:
        model = TreeNumbersListQualif
        fields = '__all__'

        # error_messages = {
        #     NON_FIELD_ERRORS: {
        #         'unique_together': "%(field_labels)s already exist.",
        #     }
        # }

    # Verifica a quantidade de caracteres e formatacao adequada
    def clean_tree_number(self):
        data = self.cleaned_data.get('tree_number')
        # print '---->',data
        tam = len(data)
        # print 'tam-->',tam

        # Nunca podera ser de tamanho PAR
        if int(tam) % 2 == 0:
            # print 'Par'
            message = _("Format")
            self.add_error('tree_number', message)
        else:
            # Se for IMPAR será verificado a quantidade de pontos existentes
            # print 'Impar'
            qtd_pontos_esperado = ((tam + 1) / 4) - 1
            # print 'Qtd pontos esperado',qtd_pontos_esperado

            tponto = 0
            for letra in data:
                # print 'letra -> ',letra
                if letra == '.':
                    tponto = tponto + 1

            # print 'Qtd pontos existentes', tponto
            if qtd_pontos_esperado != tponto:
                message = _("Format")
                self.add_error('tree_number', message)

        # Força que seja maiusculo
        upper_data = data.upper()
        # print 'M -->',upper_data
        data = upper_data

        return data


# Concept + Term - Form2
class IdentifierConceptListQualifForm(forms.ModelForm):
    class Meta:
        model = IdentifierConceptListQualif
        fields = '__all__'

class ConceptListQualifForm(forms.ModelForm):
    class Meta:
        model = ConceptListQualif
        fields = '__all__'

class TermListQualifForm(forms.ModelForm):
    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_altered = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date altered"), required=False)

    class Meta:
        model = TermListQualif
        fields = '__all__'

# Processos a parte
class TermListQualifUniqueForm(forms.ModelForm):
    class Meta:
        model = TermListQualif
        exclude = ('identifier',)

    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_altered = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date altered"), required=False)


class legacyInformationQualifForm(forms.ModelForm):
    class Meta:
        model = legacyInformationQualif
        exclude = ('identifier',)



# Descriptor ------------------------------------------------------------------

# Register - Form1
class IdentifierDescForm(forms.ModelForm):

    class Meta:
        model = IdentifierDesc
        fields = '__all__'

    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_revised = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date revised"), required=False)
    date_established = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date established"), required=False)

    # Utilizado para pre filtrar abbreviation com registros especificos do tesauro escolhido
    def __init__(self, *args, **kwargs):
        self.ths = kwargs.pop('ths', None)
        # print self.ths
        super(IdentifierDescForm, self).__init__(*args, **kwargs)
        self.fields['abbreviation'].queryset = IdentifierQualif.objects.filter(thesaurus=self.ths)


class DescriptionDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }


class TreeNumbersListDescForm(forms.ModelForm):

    # tree_number = forms.CharField(widget=widgets.TextInput(attrs={'required': True}))

    class Meta:
        fields = '__all__'

    # Verifica a quantidade de caracteres e formatacao adequada
    def clean_tree_number(self):
        data = self.cleaned_data.get('tree_number')
        # print 'Data --->',data
        tam = len(data)
        # Nunca podera ser de tamanho PAR
        if int(tam) % 2 == 0:
            # print 'Par'
            message = _("Format")
            self.add_error('tree_number', message)
        else:
            # Se for IMPAR será verificado a quantidade de pontos existentes
            # print 'Impar'
            qtd_pontos_esperado = ((tam + 1) / 4) - 1
            # print 'Qtd pontos esperado',qtd_pontos_esperado

            tponto = 0
            for letra in data:
                # print 'letra -> ',letra
                if letra == '.':
                    tponto = tponto + 1

            # print 'Qtd pontos existentes', tponto
            if qtd_pontos_esperado != tponto:
                message = _("Format")
                self.add_error('tree_number', message)

        # Força que seja maiusculo
        upper_data = data.upper()
        # print 'M -->',upper_data
        data = upper_data

        return data


class PharmacologicalActionListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }


class SeeRelatedListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }

class PreviousIndexingListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }

class legacyInformationDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }

class EntryCombinationListDescForm(forms.ModelForm):
    class Meta:
        fields = '__all__'

        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(field_labels)s already exist.",
            }
        }




# Concept + Term - Form2
class IdentifierConceptListDescForm(forms.ModelForm):
    class Meta:
        model = IdentifierConceptListDesc
        fields = '__all__'

class ConceptListDescForm(forms.ModelForm):
    class Meta:
        Model = ConceptListDesc
        fields = '__all__'

class TermListDescForm(forms.ModelForm):
    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_altered = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date altered"), required=False)

    class Meta:
        Model = TermListDesc
        fields = '__all__'




# Processos a parte
class TermListDescUniqueForm(forms.ModelForm):
    class Meta:
        model = TermListDesc
        exclude = ('identifier',)

    date_created = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date created"), required=False)
    date_altered = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Date altered"), required=False)

class TheraurusOccurrenceListDescForm(forms.ModelForm):
    class Meta:
        model = TheraurusOccurrenceListDesc
        fields = '__all__'





class legacyInformationDescForm(forms.ModelForm):
    class Meta:
        model = legacyInformationDesc
        exclude = ('identifier',)




# FormSets
# Descriptor ------------------------------------------------------------------
# Register - Form1
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

PharmacologicalActionListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    PharmacologicalActionList,
    form=PharmacologicalActionListDescForm,
    fields='__all__',
    extra=1
    )

SeeRelatedListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    SeeRelatedListDesc,
    form=SeeRelatedListDescForm,
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

legacyInformationDescFormSet = inlineformset_factory(
    IdentifierDesc,
    legacyInformationDesc,
    form=legacyInformationDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

EntryCombinationListDescFormSet = inlineformset_factory(
    IdentifierDesc,
    EntryCombinationListDesc,
    form=EntryCombinationListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )



# Concept + Term - Form2
ConceptListDescFormSet = inlineformset_factory(
    IdentifierConceptListDesc,
    ConceptListDesc,
    form=ConceptListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

TermListDescFormSet = inlineformset_factory(
    IdentifierConceptListDesc,
    TermListDesc,
    form=TermListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )


# This form works with the form TermListDescForm
TheraurusOccurrenceListDescFormSet = inlineformset_factory(
    TermListDesc,
    TheraurusOccurrenceListDesc,
    form=TheraurusOccurrenceListDescForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )




# Qualifiers ------------------------------------------------------------------
# Register - Form1
DescriptionQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    DescriptionQualif,
    form=DescriptionQualifForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

TreeNumbersListQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    TreeNumbersListQualif,
    form=TreeNumbersListQualifForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

legacyInformationQualifFormSet = inlineformset_factory(
    IdentifierQualif,
    legacyInformationQualif,
    form=legacyInformationQualifForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )


# Concept + Term - Form2
ConceptListQualifFormSet = inlineformset_factory(
    IdentifierConceptListQualif,
    ConceptListQualif,
    form=ConceptListQualifForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

TermListQualifFormSet = inlineformset_factory(
    IdentifierConceptListQualif,
    TermListQualif,
    form=TermListQualifForm,
    fields='__all__',
    can_delete=True,
    extra=1
    )

