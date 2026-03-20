from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from main.models import Descriptor, Keyword, ResourceThematic
from attachments.models import Attachment

from utils.forms import BaseDescriptorInlineFormSet, DescriptorForm, ResourceThematicRequired
from oer.models import *

import simplejson

class OERForm(forms.ModelForm):

    class Meta:
        model = OER
        exclude = ('cooperative_center_code', 'cvsp_node')
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(OERForm, self).__init__(*args, **kwargs)

        if self.user_data['service_role'].get('OER') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()

    def clean(self):
        data = self.cleaned_data
        status = data.get('status')
        required_fields = ['learning_objectives', 'description', 'creator', 'type', 'language',
                           'license', 'learning_context']

        for field in required_fields:
            value = data[field]

            if status == 1 and not value:
                self.add_error(field, _("Required for publication"))

        return data


    def save(self, *args, **kwargs):
        obj = super(OERForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # add information about cvsp node based on user network (ex. CVSP-OPS ==> cvsp_node = ops)
        if not obj.cvsp_node:
            user_network = self.user_data['networks']
            cvsp_network = next((node for node in user_network if node.startswith('CVSP')), None)
            if cvsp_network:
                cvsp_node = cvsp_network.split("-",1)[1]
                cvsp_node = cvsp_node.lower()

                obj.cvsp_node = cvsp_node

        # save modifications
        obj.save()

        return obj


class ThematicForm(forms.ModelForm):

    def save(self, *args, **kwargs):
        obj = super(ThematicForm, self).save(commit=False)
        # for legislation default value for descriptor is admited
        obj.status = 1
        obj.save()


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput)

    def clean_attachment_file(self):
        data = self.cleaned_data['attachment_file']
        if data.size > int(settings.MAX_UPLOAD_SIZE):
            raise forms.ValidationError(_('Maximum allowed size %(max)s. Current filesize %(size)s') % ({
                                           'max': filesizeformat(settings.MAX_UPLOAD_SIZE),
                                           'size': filesizeformat(data.size)
                                           }))

        return data


class URLForm(forms.ModelForm):
    url = forms.URLField(widget=widgets.URLInput(attrs={'class': 'input-xxlarge'}))


# definition of inline formsets
DescriptorFormSet = generic_inlineformset_factory(
    Descriptor,
    form=DescriptorForm,
    formset=BaseDescriptorInlineFormSet,
    exclude=('status',),
    can_delete=True,
    extra=1
)

AttachmentFormSet = generic_inlineformset_factory(
    Attachment,
    form=AttachmentForm,
    exclude=('short_url',),
    can_delete=True,
    extra=1
)

URLFormSet = inlineformset_factory(
    OER,
    OERURL,
    form=URLForm,
    fields='__all__',
    can_delete=True,
    extra=1
)

RelationFormSet = inlineformset_factory(
    OER,
    Relationship,
    fields='__all__',
    fk_name='oer_related',
    can_delete=True,
    extra=1
)

ResourceThematicFormSet = generic_inlineformset_factory(
    ResourceThematic,
    form=ThematicForm,
    exclude=('status',),
    can_delete=True,
    extra=1
)
