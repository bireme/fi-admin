# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

language_choices = (('pt', 'Português'), ('es', 'Espanhol'),
               ('en', 'Inglês'))


class CallNumberAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Center code'), missing=unicode(''))
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Classification number'), missing=unicode(''))
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Author number'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Volumen, inventory number, part'), missing=unicode(''),)
    _t = colander.SchemaNode(colander.String('utf-8'), title=_('Lending system'), missing=unicode(''),)


class CallNumber(colander.SequenceSchema):
    item = CallNumberAttributes(
)


class ElectronicAddressAttributes(colander.MappingSchema):
    _u = colander.SchemaNode(colander.String('utf-8'), title=_('Electric address'))
    _i = colander.SchemaNode(colander.String('utf-8'),
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Language'))
    _g = colander.SchemaNode(colander.String('utf-8'), title=_('Fulltext'), missing=unicode(''),)
    _k = colander.SchemaNode(colander.String('utf-8'), title=_('Password'), missing=unicode(''),)
    _l = colander.SchemaNode(colander.String('utf-8'), title=_('Logon'), missing=unicode(''),)
    _q = colander.SchemaNode(colander.String('utf-8'), title=_('File extension'), missing=unicode(''),)
    _s = colander.SchemaNode(colander.String('utf-8'), title=_('File length'), missing=unicode(''),)
    _x = colander.SchemaNode(colander.String('utf-8'), title=_('No public note'), missing=unicode(''),)
    _y = colander.SchemaNode(colander.String('utf-8'), title=_('File type'), missing=unicode(''),)
    _z = colander.SchemaNode(colander.String('utf-8'), title=_('Public note'), missing=unicode(''),)


class ElectronicAddress(colander.SequenceSchema):
    item = ElectronicAddressAttributes()


class TitleAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Title'))
    _i = colander.SchemaNode(colander.String('utf-8'),
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Language'))

class Title(colander.SequenceSchema):
    title = TitleAttributes()


class IndividualAuthorAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Personal author'))
    _1 = colander.SchemaNode(colander.String('utf-8'),
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Affiliation institution level 1'))
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'), missing=unicode(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'), missing=unicode(''),)


class IndividualAuthor(colander.SequenceSchema):
    item =IndividualAuthorAttributes()


class CorporateAuthorAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Corporate author'))
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Degree of responsibility'), missing=unicode(''),)


class CorporateAuthor(colander.SequenceSchema):
    item = CorporateAuthorAttributes()



class DescriptiveInformationAttributes(colander.MappingSchema):
    _b = colander.SchemaNode(colander.String('utf-8'), title=_('Other physical details'), missing=unicode(''),)
    _a = colander.SchemaNode(colander.String('utf-8'), title=_('Item extension'), missing=unicode(''),)
    _c = colander.SchemaNode(colander.String('utf-8'), title=_('Dimension'), missing=unicode(''),)
    _e = colander.SchemaNode(colander.String('utf-8'), title=_('Accompanying material'), missing=unicode(''),)


class DescriptiveInformation(colander.SequenceSchema):
    item = DescriptiveInformationAttributes()

class ThesisDissertationLeaderAttributes(colander.MappingSchema):
    text = colander.SchemaNode(colander.String('utf-8'), title=_('Personal author'))
    _1 = colander.SchemaNode(colander.String('utf-8'),
                    widget=deform.widget.SelectWidget(values=language_choices),
                    title=_('Affiliation institution level 1'))
    _2 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 2'), missing=unicode(''),)
    _3 = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation institution level 3'), missing=unicode(''),)
    _p = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation country'), missing=unicode(''),)
    _r = colander.SchemaNode(colander.String('utf-8'), title=_('Affiliation degree of responsibility'), missing=unicode(''),)


class ThesisDissertationLeader(colander.SequenceSchema):
    item = ThesisDissertationLeaderAttributes()
