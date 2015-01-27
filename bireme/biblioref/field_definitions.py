# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

language_choices = (('pt', 'Português'), ('es', 'Espanhol'),
               ('en', 'Inglês'))



class ElectronicAddressAttributes(colander.MappingSchema):
    u = colander.SchemaNode(colander.String('utf-8'), title=_('Electric address'))
    i = colander.SchemaNode(colander.String('utf-8'), 
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Language'))
    g = colander.SchemaNode(colander.String('utf-8'), title=_('Fulltext'), missing=unicode(''),)
    k = colander.SchemaNode(colander.String('utf-8'), title=_('Password'), missing=unicode(''),)
    l = colander.SchemaNode(colander.String('utf-8'), title=_('Logon'), missing=unicode(''),)
    q = colander.SchemaNode(colander.String('utf-8'), title=_('File extension'), missing=unicode(''),)
    s = colander.SchemaNode(colander.String('utf-8'), title=_('File length'), missing=unicode(''),)
    x = colander.SchemaNode(colander.String('utf-8'), title=_('No public note'), missing=unicode(''),)
    y = colander.SchemaNode(colander.String('utf-8'), title=_('File type'), missing=unicode(''),)
    z = colander.SchemaNode(colander.String('utf-8'), title=_('Public note'), missing=unicode(''),)


class ElectronicAddress(colander.SequenceSchema):
    item = ElectronicAddressAttributes()


class TitleAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'))
    language = colander.SchemaNode(colander.String('utf-8'), 
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Language'))

class Title(colander.SequenceSchema):
    title = TitleAttributes()


