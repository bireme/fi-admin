# coding: utf-8

from django.utils.translation import ugettext_lazy as _

############################## Title Choices ##############################

PUBLICATION_LEVEL_CHOICES = (
    ('CT', _('Scientific/Technical')),
    ('DI', _('Disclosure')),
)

TITLE_VARIANCE_CHOICES = (
    ('230', _('Parallel title')),
    ('235', _('Shortened parallel title')),
    ('240', _('Other title forms')),
)

ACQUISITION_PRIORITY_CHOICES = (
    ('1', _('Indispensable')),
    ('2', _('Dispensable (exists in the country)')),
    ('3', _('Dispensable (exists in the region)')),
)

ACQUISITION_FORM_CHOICES = (
    ('0', 'Unknown'),
    ('1A', 'Purchase current'),
    ('1B', 'Purchase canceled'),
    ('2A', 'Exchange current'),
    ('2B', 'Exchange canceled'),
    ('3A', 'Donation current'),
    ('3B', 'Donation canceled'),
)

TITLE_ALPHABET_CHOICES = (
    ('A', _('Basic roman')),
    ('B', _('Extended roman')),
    ('C', _('Cyrillic')),
    ('D', _('Japanese')),
    ('E', _('Chinese')),
    ('K', _('Korean')),
    ('F', _('Arabic')),
    ('G', _('Greek')),
    ('H', _('Hebrew')),
    ('I', _('Thai')),
    ('J', _('Devanagari')),
    ('L', _('Tamil')),
    ('Z', _('Others')),
)

FREQUENCY_CHOICES = (
    ('A', _('Annual')),
    ('B', _('Bimonthly (every two months)')),
    ('C', _('Biweekly (twice per week)')),
    ('D', _('Daily')),
    ('E', _('Fortnightly (every two weeks)')),
    ('F', _('Semiannual/Biannual')),
    ('G', _('Biennial (every two years)')),
    ('H', _('Triennial (every three years)')),
    ('I', _('Three times a week')),
    ('J', _('Three times a month')),
    ('K', _('Irregular')),
    ('M', _('Monthly')),
    ('Q', _('Quarterly (four times a year)')),
    ('S', _('Semimonthly (twice per month)')),
    ('T', _('Triannual (three times a year)')),
    ('W', _('Weekly')),
    ('Z', _('Other frequencies')),
    ('?', _('Unknown frequency')),
)

AUDIT_CHOICES = (
    ('510', _('Has edition in another language')),
    ('520', _('It is edition in another language')),
    ('530', _('Has subseries')),
    ('540', _('It is subseries of')),
    ('550', _('Has supplement or insertion')),
    ('560', _('It is supplement or insertion')),
    ('610', _('Continuation of')),
    ('620', _('Partial continuation of')),
    ('650', _('Absorbed')),
    ('660', _('Absorbed in part')),
    ('670', _('Formed by subdivision of')),
    ('680', _('Fusion of...with...')),
    ('710', _('Continued by')),
    ('720', _('Continued in part by')),
    ('750', _('Absorbed by')),
    ('760', _('Absorbed in part by')),
    ('770', _('Subdivided into')),
    ('780', _('Merged with')),
    ('790', _('To form')),
)

STATE_CHOICES = (
    ("AC", "Acre"),
    ("AL", "Alagoas"),
    ("AM", "Amazonas"),
    ("AP", "Amapá"),
    ("BA", "Bahia"),
    ("CE", "Ceará"),
    ("DF", "Distrito Federal"),
    ("ES", "Espírito Santo"),
    ("GO", "Goiás"),
    ("MA", "Maranhão"),
    ("MT", "Mato Grosso"),
    ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"),
    ("PA", "Pará"),
    ("PB", "Paraíba"),
    ("PR", "Paraná"),
    ("PE", "Pernambuco"),
    ("PI", "Piauí"),
    ("RJ", "Rio de Janeiro"),
    ("RN", "Rio Grande do Norte"),
    ("RO", "Rondônia"),
    ("RS", "Rio Grande do Sul"),
    ("RR", "Roraima"),
    ("SC", "Santa Catarina"),
    ("SE", "Sergipe"),
    ("SP", "São Paulo"),
    ("TO", "Tocantins"),
)

ACCESS_TYPE_CHOICES = (
    ("ALIV", _("Free")),
    ("ALAP", _("Free for subscribers")),
    ("AAEL", _("Requires ONLINE subscription")),
    ("ACOP",_ ("Requires ONLINE/PRINT subscription")),
)

ACCESS_CONTROL_CHOICES = (
    ("LIVRE", _("Free")),
    ("IP", _("IP")),
    ("PASS", _("Password")),
    ("IP/PASS",_ ("IP/Password")),
)
