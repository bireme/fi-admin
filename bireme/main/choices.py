# coding: utf-8

from django.utils.translation import ugettext_lazy as _

LANGUAGES_CHOICES = (
    ('en', _('English')), # default language
    ('pt-br', _('Portuguese')),
    ('es', _('Spanish')),
)

######################################################## Descriptor choices ###

DESCRIPTOR_LEVEL = [
    ('general', _('General')),
    ('specific', _('Specific')),
    ('geographic', _('Geographic')),
]

DESCRIPTOR_VOCABULARY = [
    ('DeCS', _('DeCS: Health Sciences Descriptors')),
    ('Kewords', _('Keywords')),
]

