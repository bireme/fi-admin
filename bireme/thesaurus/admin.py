# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from .models_thesaurus import *
from .models_qualifiers import *
from .models_descriptors import *

models = [
            Thesaurus, 
            IdentifierQualif,
            DescriptionQualif,
            TreeNumbersListQualif,
            TermListQualif,
            IdentifierDesc,
            DescriptionDesc,
            TreeNumbersListDesc,
            PreviousIndexingListDesc,
            ConceptListDesc,
            TermListDesc,
         ]

admin.site.register(models)

