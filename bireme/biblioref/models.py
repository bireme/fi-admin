#! coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.db import models
from utils.fields import JSONField
from utils.models import Generic
from main import choices


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

    title = JSONField(_('Title'), blank=True, dump_kwargs={'ensure_ascii': False})
    
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    def __unicode__(self):
        
        metadata_json = self.title
        return metadata_json[0]['text']
        

