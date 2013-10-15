from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django import forms

from models import *

class SuggestResourceForm(forms.ModelForm):

    class Meta:
        model = SuggestResource
        fields = ['title', 'link',]


    def clean_title(self):
        data = self.cleaned_data['title']

        if len(data) < 5:
            raise forms.ValidationError( _("Title too short") )

        # Always return the cleaned data, whether you have changed it or not.
        return data