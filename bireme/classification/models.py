#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from django.db import models
from log.models import AuditLog

from main.choices import LANGUAGES_CHOICES

# Classification types
class Type(models.Model):

    class Meta:
        verbose_name = _("Classification type")
        verbose_name_plural = _("Classification types")

    name = models.CharField(_("Name"), max_length=74)

    def __unicode__(self):
        return self.name


# Term
class Term(models.Model, AuditLog):
    class Meta:
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")

    type = models.ForeignKey(Type, verbose_name=_("Type"))
    name = models.CharField(_("Name"), max_length=155, blank=True)
    slug = models.SlugField(_("Slug"), max_length=155, blank=True)
    parent = models.ForeignKey('self', verbose_name=_("Parent"), null=True, blank=True)

    def get_children(self, *args, **kwargs):
        children = Term.objects.filter(parent=self.id)

        return children

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Term, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class TermLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    term = models.ForeignKey(Term, verbose_name=_("Term"))
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=155)


# Relationship Object x Term
class Relationship(models.Model):

    class Meta:
        unique_together = (('object_id', 'content_type', 'term'),)

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='relationship')
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    term = models.ForeignKey(Term, verbose_name=_("Term"))

    def __unicode__(self):
        return unicode(self.term)
