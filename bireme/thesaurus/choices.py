# coding: utf-8

from django.utils.translation import ugettext_lazy as _


############################## Thesaurus Choices ##############################


LANGUAGE_CODE_MESH=(
            ('en', _("English")),
            ('es', _("Spanish Latin America")),
            ('pt-br', _("Portuguese")),
            ('es-es', _("Spanish Spain")),
            ('fr', _("French")),
)


YN_OPTION=(
    ('Y','Yes'),('N','No')
)


DESCRIPTOR_CLASS_CODE=(
            ('1', _("1 - Topical Descriptor")),
            ('2', _("2 - Publication Types, for example Review")),
            ('3', _("3 - Check Tag, e.g., Male - no tree number")),
            ('4', _("4 - Geographic Descriptor")),
)


# RELATION_NAME_OPTION=(
#     ('BRD','BRD - Broader'),
#     ('NRW','NRW - Narrower'),
#     ('REL','REL - Related but not broader or narrower'),
# )


LEXICALTAG_OPTION=(
    ('ABB','ABB - Abbreviation'),
    ('ABX','ABX - Embedded abbreviation'),
    ('ACR','ACR - Acronym'),
    ('ACX','ACX - Embedded acronym'),
    ('EPO','EPO - Eponym'),
    ('LAB','LAB - Lab number'),
    ('NAM','NAM - Proper name'),
    ('NON','NON - None'),
    ('TRD','TRD - Trade name'),
)