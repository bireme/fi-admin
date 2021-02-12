from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django import forms

from error_reporting.models import *

class ErrorReportForm(forms.ModelForm):

    class Meta:
        model = ErrorReport
        exclude = ('object_id','content_type',)


class ExternalErrorReportForm(forms.ModelForm):
    class Meta:
        model = ErrorReport
        exclude = ('status','object_id','content_type',)
