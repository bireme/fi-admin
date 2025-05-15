from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from  django.contrib.contenttypes.forms import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from main.models import Descriptor, Keyword, ResourceThematic
from attachments.models import Attachment
from utils.models import AuxCode

from utils.forms import BaseDescriptorInlineFormSet, ResourceThematicRequired

from multimedia.models import *

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


class AttachmentForm(forms.ModelForm):
    # change widget from attachment_file field for simple select
    attachment_file = forms.FileField(widget=widgets.FileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # change the default values for the language field for the text_language AuxCode
        blank_option = [('', '---------')]
        language_choices = [
            (lang.code if lang.code != 'pt' else 'pt-br', lang)
            for lang in AuxCode.objects.filter(field='text_language')
        ]
        # replace the auto‐generated CharField with ChoiceField
        self.fields['language'] = forms.ChoiceField(
            choices=blank_option + language_choices,
            widget=forms.Select(attrs={'class': 'input_select_text_language'}),
            label=self.fields['language'].label,
            required=self.fields['language'].required,
        )


    def clean_attachment_file(self):
        data = self.cleaned_data['attachment_file']
        if data.size > int(settings.MAX_UPLOAD_SIZE):
            raise forms.ValidationError(_('Maximum allowed size %(max)s. Current filesize %(size)s') % ({
                                           'max': filesizeformat(settings.MAX_UPLOAD_SIZE),
                                           'size': filesizeformat(data.size)
                                           }))

        return data


# definition of inline formsets

DescriptorFormSet = generic_inlineformset_factory(Descriptor, formset=BaseDescriptorInlineFormSet, exclude=('primary', 'status',),
                                                  can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, exclude=('status',), can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, exclude=('status',),
                                                        can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(MediaType, MediaTypeLocal, fields='__all__',
                                               can_delete=True, extra=1)

MediaCollectionTranslationFormSet = inlineformset_factory(MediaCollection, MediaCollectionLocal,
                                                          fields='__all__', can_delete=True, extra=1)

AttachmentFormSet = generic_inlineformset_factory(Attachment, form=AttachmentForm,
                                                  exclude=('short_url',), can_delete=True, extra=1)
