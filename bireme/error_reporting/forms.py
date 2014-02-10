from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django import forms

from models import *

class ErrorReportForm(forms.ModelForm):

    class Meta:
        model = ErrorReport
        exclude = ('object_id','content_type',)


class ExternalErrorReportForm(forms.ModelForm):
    class Meta:
        model = ErrorReport
        exclude = ('status',)

    def clean_title(self):
        data = self.cleaned_data['title']

        if len(data) < 5:
            raise forms.ValidationError( _("Title too short") )

        # Always return the cleaned data, whether you have changed it or not.
        return data
