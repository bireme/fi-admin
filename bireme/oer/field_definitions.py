# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from main.models import SourceLanguage
from utils.models import AuxCode, Country

import colander
import deform
import json

language_choices = [('', '')] + [(aux.code, aux) for aux in AuxCode.objects.filter(field='text_language')]

def get_aux_country_list():
    country_list = [('', '')]
    country_list_latin_caribbean = [(c.code, str(c)) for c in Country.objects.filter(LA_Caribbean=True)]
    country_list_other = [(c.code, str(c)) for c in Country.objects.filter(LA_Caribbean=False)]

    # sort list by translation name
    country_list_latin_caribbean.sort(key=lambda c: c[1])
    country_list_other.sort(key=lambda c: c[1])

    separator = " ----------- "
    label_latin_caribbean = separator + __('Latin America & Caribbean') + separator
    label_other = separator + __('Others') + separator

    country_list.extend([(' ', label_latin_caribbean)])
    country_list.extend(country_list_latin_caribbean)
    country_list.extend([(' ', label_other)])
    country_list.extend(country_list_other)

    return country_list

class AuthorAttributes(colander.MappingSchema):
    degree_choices = [('', '')]
    degree_choices.extend([(aux.code, aux) for aux in
                          AuxCode.objects.filter(field='degree_of_responsibility')])

    countries_choices = get_aux_country_list()

    text = colander.SchemaNode(colander.String('utf-8'), title=_('Name'),
                               description=_('Inform individual or institutional name'))
    _1 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 1'), missing=str(''),)
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=str(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=str(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation city'), missing=str(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'),
                             widget=deform.widget.SelectWidget(values=countries_choices), missing=str(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'),
                             widget=deform.widget.SelectWidget(values=degree_choices),
                             missing=str(''),)


class Creator(colander.SequenceSchema):
    item = AuthorAttributes(title=_('Creator'))


class Contributor(colander.SequenceSchema):
    item = AuthorAttributes(title=_('Contributor'))
