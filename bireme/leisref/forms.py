from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.db.models import Q
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from main.models import Descriptor, Keyword, ResourceThematic
from attachments.models import Attachment

from utils.forms import BaseDescriptorInlineFormSet, ResourceThematicRequired
from models import *

import simplejson

class ActForm(forms.ModelForm):

    class Meta:
        model = Act
        exclude = ('organ_issuer', 'cooperative_center_code',)
        fields = '__all__'

    issue_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), required=False,
                                 input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Issue date"))
    publication_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'), required=False,
                                       input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY', label=_("Publication date"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(ActForm, self).__init__(*args, **kwargs)

        # context options lists based on act scope region
        if self.instance.id and self.instance.scope_region:
            region_id = self.instance.scope_region
            first_option = [('', '----------')]

            # create context lists and sort by name
            type_choices = [(s.id, unicode(s)) for s in ActType.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
            type_choices.sort(key=lambda tup: tup[1])
            scope_choices = [(s.id, unicode(s)) for s in ActScope.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
            scope_choices.sort(key=lambda tup: tup[1])
            source_choices = [(s.id, unicode(s)) for s in ActSource.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
            source_choices.sort(key=lambda tup: tup[1])
            organ_choices = [(s.id, unicode(s)) for s in ActOrganIssuer.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
            organ_choices.sort(key=lambda tup: tup[1])
            state_choices = [(s.id, unicode(s)) for s in ActState.objects.filter(scope_region=region_id)]
            state_choices.sort(key=lambda tup: tup[1])
            city_choices = [(s.id, unicode(s)) for s in ActCity.objects.filter(scope_region=region_id)]
            city_choices.sort(key=lambda tup: tup[1])
            collection_choices = [(s.id, unicode(s)) for s in ActCollection.objects.all()]
            collection_choices.sort(key=lambda tup: tup[1])

            self.fields['act_type'].choices = first_option + type_choices
            self.fields['scope'].choices = first_option + scope_choices
            self.fields['source_name'].choices = first_option + source_choices
            self.fields['issuer_organ'].choices = first_option + organ_choices
            self.fields['scope_state'].choices = first_option + state_choices
            self.fields['scope_city'].choices = first_option + city_choices
            self.fields['act_collection'].choices = first_option + collection_choices
        else:
            empty_list = [('', '')]
            self.fields['act_type'].choices = empty_list
            self.fields['scope'].choices = empty_list
            self.fields['source_name'].choices = empty_list
            self.fields['issuer_organ'].choices = empty_list
            self.fields['scope_state'].choices = empty_list
            self.fields['scope_city'].choices = empty_list
            self.fields['act_collection'].choices = empty_list

        self.fields['issue_date'].widget.attrs['class'] = 'datepicker'
        self.fields['publication_date'].widget.attrs['class'] = 'datepicker'

        if self.user_data['service_role'].get('LeisRef') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()

    def save(self, *args, **kwargs):
        obj = super(ActForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # save modifications
        obj.save()

        return obj


class DescriptorForm(forms.ModelForm):
    def save(self, *args, **kwargs):
        obj = super(DescriptorForm, self).save(commit=False)
        # for legislation default value for descriptor is admited
        obj.status = 1
        obj.save()


class ThematicForm(forms.ModelForm):

    status = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    def save(self, *args, **kwargs):
        obj = super(ThematicForm, self).save(commit=False)
        # for legislation default value for descriptor is admited
        obj.status = 1
        obj.save()


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput(attrs={'class': 'input-xxlarge'}))


class URLForm(forms.ModelForm):
    # add class to field
    url = forms.URLField(widget=widgets.URLInput(attrs={'class': 'input-xxlarge'}))



class ActRelatedForm(forms.ModelForm):

    class Meta:
        model = Act
        fields = ('status', 'scope_region', 'act_type', 'act_number', 'denomination', 'issue_date')

    issue_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                 input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(
    Descriptor,
    form=DescriptorForm,
    formset=BaseDescriptorInlineFormSet,
    exclude=('status',),
    can_delete=True,
    extra=1
)

AttachmentFormSet = generic_inlineformset_factory(Attachment, form=AttachmentForm,
                                                  exclude=('short_url',), can_delete=True, extra=1)

URLFormSet = inlineformset_factory(Act, ActURL, form=URLForm, fields='__all__', can_delete=True, extra=1)

RelationFormSet = inlineformset_factory(Act, ActRelationship, fields='__all__', fk_name='act_related',
                                        can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, form=ThematicForm,
                                                        can_delete=True, extra=1)

CountryRegionTranslationFormSet = inlineformset_factory(ActCountryRegion, ActCountryRegionLocal, fields='__all__',
                                                        can_delete=True, extra=1)

ActScopeTranslationFormSet = inlineformset_factory(ActScope, ActScopeLocal, fields='__all__',
                                                   can_delete=True, extra=1)

ActTypeTranslationFormSet = inlineformset_factory(ActType, ActTypeLocal, fields='__all__',
                                                  can_delete=True, extra=1)

ActOrganTranslationFormSet = inlineformset_factory(ActOrganIssuer, ActOrganIssuerLocal, fields='__all__',
                                                   can_delete=True, extra=1)

ActSourceTranslationFormSet = inlineformset_factory(ActSource, ActSourceLocal, fields='__all__',
                                                    can_delete=True, extra=1)

ActRelTypeTranslationFormSet = inlineformset_factory(ActRelationType, ActRelationTypeLocal, fields='__all__',
                                                     can_delete=True, extra=1)

ActStateTranslationFormSet = inlineformset_factory(ActState, ActStateLocal, fields='__all__',
                                                    can_delete=True, extra=1)

ActCityTranslationFormSet = inlineformset_factory(ActCity, ActCityLocal, fields='__all__',
                                                   can_delete=True, extra=1)

ActCollectionTranslationFormSet = inlineformset_factory(ActCollection, ActCollectionLocal, fields='__all__',
                                                         can_delete=True, extra=1)
