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
    ('Y',_('Yes')),('N',_('No'))
)


DESCRIPTOR_CLASS_CODE=(
            ('1', _("1 - Topical Descriptor")),
            ('2', _("2 - Publication Types, for example Review")),
            ('3', _("3 - Check Tag, e.g., Male - no tree number")),
            ('4', _("4 - Geographic Descriptor")),
)


RELATION_NAME_OPTION=(
    ('NRW',_("NRW - Narrower")),
    ('BRD',_("BRD - Broader")),
    ('REL',_("REL - Related but not broader or narrower")),
)


LEXICALTAG_OPTION=(
    ('ABB',_('ABB - Abbreviation')),
    ('ABX',_('ABX - Embedded abbreviation')),
    ('ACR',_('ACR - Acronym')),
    ('ACX',_('ACX - Embedded acronym')),
    ('EPO',_('EPO - Eponym')),
    ('LAB',_('LAB - Lab number')),
    ('NAM',_('NAM - Proper name')),
    ('NON',_('NON - None')),
    ('TRD',_('TRD - Trade name')),
)


STATUS_CHOICES=(
    # (-3, _('Migration')),
    (-1, _('Draft')),
    (1, _('Published')),
    (3, _('Deleted')),
    (5, _('Historical')),
    (10, _('Awaiting translation')),
)

