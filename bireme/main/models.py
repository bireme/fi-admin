#! coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models

from utils.models import Generic

from main import choices

# Auxiliar table Type of source [318]
class SourceType(Generic):

    class Meta:
        verbose_name = _("source type")
        verbose_name_plural = _("source types")

    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def __unicode__(self):
        return unicode(self.name)

class SourceTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    source_type = models.ForeignKey(SourceType, verbose_name=_("Source type"))
    language = models.CharField(_("language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# Auxiliar table Language of source [317]
class SourceLanguage(Generic):

    class Meta:
        verbose_name = _("Source language")
        verbose_name_plural = _("Source languages")

    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def __unicode__(self):
        return unicode(self.name)

class SourceLanguageLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    source_language = models.ForeignKey(SourceLanguage, verbose_name=_("Source language"))
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

# Auxiliar table LIS type [302]
class ThematicArea(Generic):

    class Meta:
        verbose_name = _("Thematic area")
        verbose_name_plural = _("Thematic areas")

    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def __unicode__(self):
        return unicode(self.name)

class ThematicAreaLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    thematic_area = models.ForeignKey(ThematicArea, verbose_name=_("Thematic area"))
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)


# Main table
class Resource(Generic):

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")

    STATUS_CHOICES = (
        ('0', _('Pending')),
        ('1', _('Admitted')),
        ('2', _('Refused')),
        ('3', _('Deleted')),
    )

    # status (399)
    status = models.CharField(_('Status'), max_length=2, choices=STATUS_CHOICES, blank=True, null=True, default=0)

    # title (311)
    title = models.CharField(_('Title'), max_length=255)
    # link (351)
    link = models.URLField(_('Link'), max_length=255)
    # source (305)
    record_source = models.CharField(_('Record source'), max_length=255, blank=True, null=True)
    # originator (313)
    originator = models.CharField(_('Originator'), max_length=255, blank=True, null=True)
    # originator_location
    originator_location = models.CharField(_('Originator location'), max_length=255, blank=True, null=True)
    # author (315)
    author = models.CharField(_('Author'), max_length=255, blank=True, null=True)
    # language of resource (317)
    language = models.ForeignKey(SourceLanguage, verbose_name=_("Source language"), blank=True, null=True)
    # source type (318)
    source_type = models.ForeignKey(SourceType, verbose_name=_("Source type"), blank=True, null=True)
    # lis type (302)
    thematic_areas = models.ForeignKey(ThematicArea, verbose_name=_("Thematic area"), blank=True, null=True)
    # abstract (319)
    abstract = models.TextField(_("Abstract"), blank=True, null=True)
    # time period (341)
    time_period_textual = models.CharField(_('Temporal range'), max_length=255, blank=True, null=True)
    # objective (361)
    objective = models.CharField(_('Objective'), max_length=255, blank=True, null=True)
    # responsible cooperative center
    cooperative_center = models.CharField(_('Cooperative center'), max_length=55, blank=True, null=True)


    def get_fields(self):
        return [(field.verbose_name, field.value_to_string(self)) for field in Resource._meta.fields]

    def __unicode__(self):
        return unicode(self.title)


# Taxonomy table
class Descriptor(models.Model):
    class Meta:
        order_with_respect_to = 'resource'

    resource = models.ForeignKey(Resource, related_name='resources')
    vocabulary = models.CharField(_('Vocabulary'), max_length=255,
                        choices=choices.DESCRIPTOR_VOCABULARY)
    level = models.CharField(_('Level'), max_length=64,
                        choices=choices.DESCRIPTOR_LEVEL)
    text = models.CharField(_('Text'), max_length=255, blank=True)

    def __unicode__(self):
        return u'[%s] %s' % (self.vocabulary, self.text)
