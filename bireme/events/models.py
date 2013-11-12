#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone

from utils.models import Generic, Country

# Main table
class Event(Generic):

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)

    title = models.CharField(_('Title'), max_length=255, blank=False)
    start_date = models.DateField(_('Start date'), help_text=_('day/month/year'))
    end_date = models.DateField(_('End date'), help_text=_('day/month/year'))

    link = models.URLField(_('Link'), blank=True)
   
    city = models.CharField(_('City'), max_length=125, blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    official_language = models.ManyToManyField('main.SourceLanguage', verbose_name=_("Official languages"), blank=True, null=True)

    contact_email = models.EmailField(_('Contact email'), blank=True)
    contact_info = models.TextField(_("Information for contact"), blank=True)

    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    def __unicode__(self):
        return self.title

