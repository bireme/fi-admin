from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from main.models import Descriptor, Keyword, ResourceThematic
from attachments.models import Attachment

from utils.forms import DescriptorRequired, ResourceThematicRequired
from models import *

import simplejson

class ActForm(forms.ModelForm):

    class Meta:
        model = Act
        exclude = ('cooperative_center_code',)
        fields = '__all__'

    issue_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                 input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')
    publication_date = forms.DateField(widget=forms.DateInput(format='%d/%m/%Y'),
                                       input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(ActForm, self).__init__(*args, **kwargs)

        # context options lists based on act scope region
        if self.instance and self.instance.scope_region:
            region_id = self.instance.scope_region
            first_option = [('', '----------')]
            self.fields['scope'].choices = first_option + [(s.id, unicode(s)) for s in ActScope.objects.filter(scope_region=region_id)]
            self.fields['source_name'].choices = first_option + [(s.id, unicode(s)) for s in ActSource.objects.filter(scope_region=region_id)]
            self.fields['organ_issuer'].choices = first_option + [(s.id, unicode(s)) for s in ActOrganIssuer.objects.filter(scope_region=region_id)]
        else:
            empty_list = [('', '')]
            self.fields['scope'].choices = empty_list
            self.fields['source_name'].choices = empty_list
            self.fields['organ_issuer'].choices = empty_list

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
        # for bibliographic default value for descriptor is admited
        obj.status = 1
        obj.save()

class ThematicForm(forms.ModelForm):
    def save(self, *args, **kwargs):
        obj = super(ThematicForm, self).save(commit=False)
        # for bibliographic default value for descriptor is admited
        obj.status = 1
        obj.save()


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput)


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(Descriptor, form=DescriptorForm,
                                                  exclude=('status',), can_delete=True, extra=1)

AttachmentFormSet = generic_inlineformset_factory(Attachment, form=AttachmentForm,
                                                  exclude=('short_url',), can_delete=True, extra=1)

URLFormSet = inlineformset_factory(Act, ActURL, fields='__all__', can_delete=True, extra=1)

RelationFormSet = inlineformset_factory(Act, ActRelationship, fields='__all__', fk_name='act_related',
                                        can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, form=ThematicForm,
                                                        formset=ResourceThematicRequired,
                                                        exclude=('status',), can_delete=True, extra=1)
