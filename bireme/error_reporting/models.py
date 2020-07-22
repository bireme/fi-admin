#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils import timezone

from utils.models import Generic

# Error reporting  table
class ErrorReport(Generic):

    class Meta:
        verbose_name = _("Error report")
        verbose_name_plural = _("Error reports")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Fixed')),
        (2, _('Invalid')),
        (3, _('SPAM')),
    )

    ERROR_CHOICES = (
        (0, _('Invalid link')),
        (1, _('Bad content')),
        (2, _('Duplicated')),
        (3, _('Other')),
    )

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='error_reporting', on_delete=models.PROTECT)
    content_object = GenericForeignKey('content_type', 'object_id')

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, default=0)
    code = models.SmallIntegerField(_('Error type'), choices=ERROR_CHOICES, default=3)
    description = models.TextField(_('Description'), blank=True)
    new_link = models.URLField(_('New link'), blank=True)

    def __str__(self):
        return self.description
