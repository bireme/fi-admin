from django.shortcuts import get_object_or_404
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *
from main.models import Descriptor, Keyword, ResourceThematic

import simplejson

class EventForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(EventForm, self).__init__(*args, **kwargs)

        if self.user_data['user_role'] == 'doc':
            self.fields['status'].widget = widgets.HiddenInput()


    def save(self, *args, **kwargs):
        obj = super(EventForm, self).save(commit=False)

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
        model  = Event
        exclude = ('cooperative_center_code',)

        source_language = forms.MultipleChoiceField()
        event_type = forms.MultipleChoiceField()


class TypeForm(forms.ModelForm):

    class Meta:
        model = EventType


# definition of inline formsets

DescriptorFormSet = generic_inlineformset_factory(Descriptor, can_delete=True, extra=1)

KeywordFormSet = generic_inlineformset_factory(Keyword, can_delete=True, extra=1)

ResourceThematicFormSet = generic_inlineformset_factory(ResourceThematic, can_delete=True, extra=1)

TypeTranslationFormSet = inlineformset_factory(EventType, EventTypeLocal, can_delete=True, extra=1)
