#! coding: utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from datetime import date

from django.db import models
from main.choices import LANGUAGES_CHOICES
from utils.models import Generic
from short_url import encode_url

import os


def attachment_upload(instance, filename):
    """Stores the attachment in a "uploads/<app_label>/<YEAR>/<MONTH>/<primary key>/" folder"""

    current_year = date.today().year
    current_month = date.today().month
    fname, dot, extension = filename.rpartition('.')
    slug_filename = "%s.%s" % (slugify(fname), extension)

    upload_path = '%s/%s/%02d/%s/%s' % (instance.content_object._meta.app_label, current_year,
                                        current_month, instance.content_object.pk, slug_filename)

    return upload_path

class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)

class Attachment(Generic):

    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    attachment_file = models.FileField(_('Select a file'), upload_to=attachment_upload, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES, blank=False)
    short_url = models.CharField(max_length=25, blank=False)

    class Meta:
        app_label = 'attachments'
        ordering = ['-created_time']

    def __unicode__(self):
        return '%s attached %s' % (self.created_by.get_username(), self.attachment_file.name)

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        # add short_url field base on attachment PK
        if not self.short_url:
            self.short_url = encode_url(self.pk)
            self.save()


    def delete(self, *args, **kwargs):
        # remove file from file system
        os.remove(os.path.join(settings.MEDIA_ROOT, self.attachment_file.name))

        super(Attachment, self).delete(*args, **kwargs)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]
