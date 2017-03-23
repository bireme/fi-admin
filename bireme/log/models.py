from django.db import models
from utils.models import Generic
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _

REVISION_CHOICES = (
    (-1, _('Not approved')),
    (1, _('Approved')),
)

class AuditLog(object):
    '''
    Class used to mark wich models audit log of changes will be recorded
    '''
    pass


class LogReview(Generic):

    class Meta:
        verbose_name = "Log Review"
        verbose_name_plural = "Log Reviews"

    log = models.ForeignKey(LogEntry)
    status = models.SmallIntegerField(_('Status'), choices=REVISION_CHOICES, null=True)
