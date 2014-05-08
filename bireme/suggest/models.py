#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone

# Create your models here.

# Resource suggest table
class SuggestResource(models.Model):

    class Meta:
        verbose_name = _("Suggested resource")
        verbose_name_plural = _("Suggested resources")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    # status (399)
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)
    # title (311)
    title = models.CharField(_('Title'), max_length=255, blank=False)
    # link (351)
    link = models.URLField(_('Link'), blank=False)

    abstract = models.TextField(_('abstract'), blank=True)

    keywords = models.TextField(_('Keywords'), blank=True)

    administrative_comments = models.TextField(_('Administrative comments'), blank=True)

    created_time = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)

    def __unicode__(self):
        return self.title

# Event suggest table
class SuggestEvent(models.Model):

    class Meta:
        verbose_name = _("Suggested event")
        verbose_name_plural = _("Suggested events")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )
 
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)

    title = models.CharField(_('Title'), max_length=455, blank=False)
    start_date = models.DateField(_('Start date'), help_text=_('day/month/year'))
    end_date = models.DateField(_('End date'), help_text=_('day/month/year'))

    link = models.URLField(_('Link'), blank=True)
   
    city = models.CharField(_('City'), max_length=125, blank=True)

    administrative_comments = models.TextField(_('Administrative comments'), blank=True)

    created_time = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)

    def __unicode__(self):
        return self.title
