from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *
from main.models import Descriptor, Keyword, ResourceThematic

from utils.forms import DescriptorRequired, ResourceThematicRequired

import simplejson

class MediaForm(forms.ModelForm):

    class Meta:
        model = Media
        exclude = ('cooperative_center_code',)
        fields = '__all__'

        source_language = forms.MultipleChoiceField()
        Media_type = forms.MultipleChoiceField()

    publication_date = forms.DateField(label=_('Publication date'), widget=forms.DateInput(format = '%d/%m/%Y'),
                                       input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(MediaForm, self).__init__(*args, **kwargs)

        if self.user_data['service_role'].get('Multimedia') == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()


    def save(self, *args, **kwargs):
        obj = super(MediaForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # save modifications
        obj.save()

        return obj


class MediaCollectionForm(forms.ModelForm):
    class Meta:
        model  = MediaCollection
        fields = '__all__'
        exclude = ('cooperative_center_code',)


# definition of inline formsets

DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=DescriptorRequired, exclude=['primary'],
                                                  can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, fields='__all__', can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, formset=ResourceThematicRequired,
                                                        can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(MediaType, MediaTypeLocal, fields='__all__',
                                               can_delete=True, extra=1)

MediaCollectionTranslationFormSet = inlineformset_factory(MediaCollection, MediaCollectionLocal,
                                                          fields='__all__', can_delete=True, extra=1)
