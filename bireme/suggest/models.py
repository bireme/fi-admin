#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

# Create your models here.

# Main table
class SuggestResource(models.Model):

    class Meta:
        verbose_name = _("suggested resource")
        verbose_name_plural = _("suggested resources")

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


    def __unicode__(self):
        return self.title

