#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from utils.fields import JSONField, AuxiliaryChoiceField, MultipleAuxiliaryChoiceField
from utils.models import Generic

# Bibliographic References
class Reference(Generic):

    class Meta:
        verbose_name = _("Bibliographic Reference")
        verbose_name_plural = _("Bibliographic References")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    LITERATURETYPE_CHOICES = (
        ('S', _('Document published as a periodic series')),
        ('SC', _('Conference papers as a periodic series')),
        ('SCP', _('Paper of project and conference as a periodic series')),
        ('SP', _('Project paper as a periodic series')),
        ('M', _('Document published as a monograph')),
        ('MC', _('Conference paper as a monograph')),
        ('MCP', _('Paper of project and conference as a monograph')),
        ('MP', _('Project paper as a monograph ')),
        ('MS', _('Document published as a monographic series ')),
        ('MSC', _('Conference paper as a monographic series ')),
        ('MSP', _('Project paper as a monographic series')),
        ('T', _('Thesis, Dissertation (published or not) ')),
        ('TS', _('Thesis, Dissertation as a monographic series')),
        ('N', _('Non Conventional document')),
        ('NC', _('Conference paper in a non conventional format')),
        ('NP', _('Project paper in a non conventionally')),
    )

    TREATMENTLEVEL_CHOICES = (
        ('m', _('Monographic level')),
        ('mc', _('Monographic level of collection')),
        ('ms', _('Monographic level of serial')),
        ('am', _('Monographic analytical level')),
        ('amc', _('Monographic analytics level of collection')),
        ('ams', _('Monographic analytics level of serial')),
        ('as', _('Analytics level of serial')),
        ('c', _('Collection level')),
    )

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)
    # field tag 03
    call_number = JSONField(_('Call number'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 04
    database = models.TextField(_('Database'), blank=True)
    # field tag 05
    literature_type = models.CharField(_('Literature type'), choices=LITERATURETYPE_CHOICES,
        max_length=10, blank=True)
    # field tag 06
    treatment_level = models.CharField(_('Treatment level'), choices=TREATMENTLEVEL_CHOICES, 
        max_length=10, blank=True)
    # field tag 07
    inventory_number = models.TextField(_('Inventory number'), blank=True)
    # field tag 08
    electronic_address = JSONField(_('Electronic address'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 09
    record_type = AuxiliaryChoiceField(_('Record type'), max_length=10, blank=True)
    # field tags 10/16/23
    individual_author = JSONField(_('Individual author'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 11/17/24
    corporate_author = JSONField(_('Corporate author'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 13/17/26
    english_translated_title = models.CharField(_('English translated title'), max_length=400, blank=True)
    # field tag 14/20
    pages = models.CharField(_('Pages'), max_length=80, blank=True)
    # field tags 21/31
    volume = models.CharField(_('Volume'), max_length=100, blank=True)
    # field tags 12/18/25
    title = JSONField(_('Title'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tags 27
    total_number_of_volumes = models.CharField(_('Total number of volumes'), max_length=10, blank=True)
    # field tags 30
    journal_title = models.CharField(_('Journal title'), max_length=250, blank=True)
    # field tags 32
    issue_number = models.CharField(_('Issue number'), max_length=80, blank=True)
    # field tags 35
    issn = models.CharField(_('ISSN'), max_length=40, blank=True)
    # field tag 38
    descriptive_information = JSONField(_('Descriptive information'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 40
    text_language = MultipleAuxiliaryChoiceField(_('Text language'), blank=True)
    # field tag 49
    thesis_dissertation_leader = JSONField(_('Thesis, Dissertation - Leader'), blank=True, dump_kwargs={'ensure_ascii': False})
    # field tag 50
    thesis_dissertation_institution = models.CharField(_('Thesis, Dissertation - Institution'), max_length=300, blank=True)
    # field tag 51
    thesis_dissertation_academic_title = models.CharField(_('Thesis, Dissertation - Academic title'), max_length=250, blank=True)
    # field tag 52
    conference_sponsoring_institution = models.TextField(_('Conference Sponsoring Institution'), blank=True)
    # field tag 53
    conference_name = models.TextField(_('Conference name'), blank=True)
    # field tag 54
    conference_date = models.CharField(_('Conference date'), max_length=100, blank=True)
    # field tag 55
    conference_normalized_date = models.CharField(_('Conference normalized date'), max_length=100, blank=True)
    # field tag 56
    conference_city = models.CharField(_('Conference city'), max_length=100, blank=True)
    # field tag 57
    # conference_country = FIXME
    # field tag 58
    project_sponsoring_institution = models.TextField(_('Project - Sponsoring Institution'), blank=True)
    # field tag 59
    project_name = models.CharField(_('Project name'), max_length=500, blank=True)
    # field tag 61
    internal_note = models.TextField(_('Internal note'), blank=True)
    # field tag 62
    publisher = models.TextField(_('Publisher'), blank=True)
    # field tag 63
    edition = models.CharField(_('Edition'), max_length=150, blank=True)
    # field tag 64
    publication_date = models.CharField(_('Publication date'), max_length=250, blank=True)
    # field tag 65
    publication_date_normalized = models.CharField(_('Publication normalized date'), max_length=25, blank=True)
    # field tag 66
    publication_city = models.CharField(_('City of publication'), max_length=100, blank=True)
    # field tag 67
    # publication_country = FIXME
    # field tag 68
    symbol = models.TextField(_('Symbol'), blank=True)
    # field tag 69
    isbn = models.CharField(_('ISBN'), max_length=60, blank=True)
    # field tag 71
    # publication_type = FIXME
    # field tag 72
    total_number_of_references = models.CharField(_('Total number of references'), max_length=100, blank=True)
    # field tag 74
    time_limits_from = models.CharField(_('Time limits (from)'), max_length=50, blank=True)
    # field tag 75
    time_limits_to = models.CharField(_('Time limits (to)'), max_length=50, blank=True)



    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    def __unicode__(self):
        return self.title[0]['text']
        

