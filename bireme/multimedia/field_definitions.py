# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from main.models import SourceLanguage
from utils.models import AuxCode, Country

import colander
import deform
import json

language_choices = [('', '')] + [(aux.code, aux) for aux in AuxCode.objects.filter(field='text_language')]

class DescriptionTranslationsAttributes(colander.MappingSchema):
    _i = colander.SchemaNode(colander.String(), widget=deform.widget.SelectWidget(values=language_choices),
                             title=_('Language'))
    text = colander.SchemaNode(colander.String(), title=_('Description'),
                               widget=deform.widget.TextAreaWidget(rows=15, cols=120))

class DescriptionTranslations(colander.SequenceSchema):
    item = DescriptionTranslationsAttributes(title=_('Description'))