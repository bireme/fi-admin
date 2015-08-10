from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django import forms

from models import *

class SuggestResourceForm(forms.ModelForm):

    class Meta:
        model = SuggestResource


class SuggestEventForm(forms.ModelForm):

    class Meta:
        model = SuggestEvent



class ExternalSuggestResourceForm(forms.ModelForm):

    class Meta:
        model = SuggestResource
        exclude = ('status',)

    def clean_title(self):
        data = self.cleaned_data['title']

        if len(data) < 5:
            raise forms.ValidationError( _("Title too short") )

        # Always return the cleaned data, whether you have changed it or not.
        return data


class ExternalSuggestEventForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')
    end_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'),
                                    input_formats=('%d/%m/%Y',), help_text='DD/MM/YYYY')

    class Meta:
        model = SuggestEvent
        exclude = ('status',)

    def clean_title(self):
        data = self.cleaned_data['title']

        if len(data) < 5:
            raise forms.ValidationError( _("Title too short") )

        # Always return the cleaned data, whether you have changed it or not.
        return data
