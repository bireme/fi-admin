from django.shortcuts import get_object_or_404

from django.forms import widgets
from django.conf import settings
from django import forms

from django.utils.translation import ugettext_lazy as _
from models import *


class LogReviewForm(forms.ModelForm):

    class Meta:
        model = LogReview
        exclude = ('cooperative_center_code',)
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(LogReviewForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        obj = super(LogReviewForm, self).save(commit=False)

        # for fields with readonly attribute restore the original value for POST data insertions hack
        for name, field in self.fields.items():
            if hasattr(field.widget.attrs, 'readonly'):
                setattr(obj, name, field.widget.original_value)

        # save modifications
        obj.save()

        return obj
