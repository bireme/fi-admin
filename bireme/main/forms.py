from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from models import *
from django import forms


class ResourceForm(forms.ModelForm):

    class Meta:
        model = Resource
        fields = ('title', 'link', 'record_source', 'originator', 'originator_location', 'author', 
                'language', 'source_type', 'topic', 'abstract', 'thesaurus','descriptors', 'geo_descriptors',
                'keywords', 'time_period_textual', 'objective')

