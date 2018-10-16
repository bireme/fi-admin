#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from django.db import models
from log.models import AuditLog
from utils.models import Country

from main.choices import LANGUAGES_CHOICES
import os


def attachment_upload(instance, filename):

    fname, dot, extension = filename.rpartition('.')
    slug_filename = "%s.%s" % (slugify(fname), extension)

    upload_path = 'collection/image/%s' % (slug_filename)

    return upload_path

# Collection
class Collection(models.Model, AuditLog):
    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    parent = models.ForeignKey('self', verbose_name=_("Parent"), null=True, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)
    name = models.CharField(_("Name"), max_length=155, blank=True)
    slug = models.SlugField(_("Slug"), max_length=155, blank=True)
    description = models.TextField(_("Description"), blank=True)
    image = models.FileField(_("Image"), upload_to=attachment_upload, blank=True)

    def get_translations(self):
            translation_list = ["%s^%s" % (self.language, self.name.strip())]
            translation = CollectionLocal.objects.filter(collection=self.id)
            if translation:
                other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
                translation_list.extend(other_languages)

            return translation_list


    def get_children(self, *args, **kwargs):
        children = Collection.objects.filter(parent=self.id)

        return children

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class CollectionLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    collection = models.ForeignKey(Collection, verbose_name=_("Collection"))
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=155)
    description = models.TextField(_("Description"), blank=True)
    image = models.FileField(_("Image"), upload_to=attachment_upload, blank=True)


# Relationship Object x Collection
class Relationship(models.Model):

    class Meta:
        unique_together = (('object_id', 'content_type', 'collection'),)

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='relationship')
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    collection = models.ForeignKey(Collection, verbose_name=_("Collection"))

    def __unicode__(self):
        return unicode(self.collection)
