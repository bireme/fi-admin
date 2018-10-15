# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from .models_thesaurus import *
from .models_qualifiers import *
from .models_descriptors import *

models = [
            Thesaurus,

            IdentifierDesc,
            DescriptionDesc,
            TreeNumbersListDesc,
            PreviousIndexingListDesc,

            IdentifierConceptListDesc,
            ConceptListDesc,
            TermListDesc,

            IdentifierQualif,
            TermListQualif,
            ConceptListQualif,
            DescriptionQualif,
            TreeNumbersListQualif,
         ]

admin.site.register(models)

