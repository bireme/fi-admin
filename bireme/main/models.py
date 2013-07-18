#! coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models

from utils.models import Generic

from main import choices

class SourceType(Generic):

    class Meta:
        verbose_name = _("source type")
        verbose_name_plural = _("source types")

    name = models.CharField(_("name"), max_length=255)

    def __unicode__(self):
        return unicode(self.name)

class SourceTypeLocal(models.Model):

    class Meta:
        verbose_name = _("source type translation")
        verbose_name_plural = _("source type translations")

    topic = models.ForeignKey(SourceType, verbose_name=_("source type"))
    name = models.CharField(_("name"), max_length=255)
    language = models.CharField(_("language"), max_length=10, choices=choices.LANGUAGES_CHOICES[1:])


class Topic(Generic):

    class Meta:
        verbose_name = _("topic")
        verbose_name_plural = _("topics")

    name = models.CharField(_("name"), max_length=255)

    def __unicode__(self):
        return unicode(self.name)

class TopicLocal(models.Model):

    class Meta:
        verbose_name = _("topic translation")
        verbose_name_plural = _("topic translations")

    topic = models.ForeignKey(Topic, verbose_name=_("topic"))
    name = models.CharField(_("name"), max_length=255)
    language = models.CharField(_("language"), max_length=10, choices=choices.LANGUAGES_CHOICES[1:])


class Resource(Generic):

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")

    STATUS_CHOICES = (
        ('0', _('Pending')),
        ('1', _('Admitted')),
        ('2', _('Refused')),
        ('3', _('Deleted')),
    )

    # title (311)
    title = models.CharField(_('title'), max_length=255)
    # link (351)
    link = models.URLField(_('link'), max_length=255)
    # source (305)
    record_source = models.CharField(_('record source'), max_length=255, blank=True, null=True)
    # originator (313)
    originator = models.CharField(_('originator'), max_length=255, blank=True, null=True)
    # originator_location
    originator_location = models.CharField(_('originator location'), max_length=255, blank=True, null=True)
    # author (315)
    author = models.CharField(_('author'), max_length=255, blank=True, null=True)
    # language of resource (317)
    language = models.CharField(_("language"), max_length=10, choices=choices.LANGUAGES_CHOICES, blank=True, null=True)
    # source type (318)
    source_type = models.ForeignKey(SourceType, verbose_name=_("source type"), blank=True, null=True)
    # lis type (302)
    topic = models.ForeignKey(Topic, verbose_name=_("lis type"), blank=True, null=True)
    # abstract (319)
    abstract = models.TextField(_("abstract"), blank=True, null=True)
    # time period (341)
    time_period_textual = models.CharField(_('author'), max_length=255, blank=True, null=True)
    # objective (361)
    objective = models.CharField(_('objective'), max_length=255, blank=True, null=True)
    # status (399)
    status = models.CharField(_('status'), max_length=2, choices=STATUS_CHOICES, blank=True, null=True)
    # responsible cooperative center 
    cooperative_center = models.CharField(_('cooperative center'), max_length=55, blank=True, null=True)
    
    def __unicode__(self):
        return unicode(self.title)

class Descriptor(models.Model):
    class Meta:
        order_with_respect_to = 'resource'

    resource = models.ForeignKey(Resource)
    vocabulary = models.CharField(_('Vocabulary'), max_length=255,
                        choices=choices.DESCRIPTOR_VOCABULARY)
    level = models.CharField(_('Level'), max_length=64,
                        choices=choices.DESCRIPTOR_LEVEL)    
    text = models.CharField(_('Text'), max_length=255, blank=True)

    def __unicode__(self):
        return u'[%s] %s: %s' % (self.vocabulary, self.code, self.text)
