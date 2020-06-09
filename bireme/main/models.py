#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.generic import GenericRelation
from django.core.cache import cache
from log.models import AuditLog

from datetime import datetime
from django.db import models

from utils.models import Generic, Country
from error_reporting.models import ErrorReport

from main import choices

DECS = 'DeCS'
GENERAL = 'general'
PENDING = 0

# Auxiliar table Type of source [318]
class SourceType(Generic):

    class Meta:
        verbose_name = _("source type")
        verbose_name_plural = _("source types")

    acronym = models.CharField(_("Acronym"), max_length=25, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = SourceTypeLocal.objects.filter(source_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "main_sourcetype-{}-{}".format(lang_code, self.id)
        sourcetype_local = cache.get(cache_id)
        if not sourcetype_local:
            translation = SourceTypeLocal.objects.filter(source_type=self.id, language=lang_code)
            if translation:
                sourcetype_local = translation[0].name
            else:
                sourcetype_local = self.name

            cache.set(cache_id, sourcetype_local, None)

        return sourcetype_local


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

    acronym = models.CharField(_("Acronym"), max_length=25, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = SourceLanguageLocal.objects.filter(source_language=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "main_sourcelanguage-{}-{}".format(lang_code, self.id)
        sourcelanguage_local = cache.get(cache_id)
        if not sourcelanguage_local:
            translation = SourceLanguageLocal.objects.filter(source_language=self.id, language=lang_code)
            if translation:
                sourcelanguage_local = translation[0].name
            else:
                sourcelanguage_local = self.name

            cache.set(cache_id, sourcelanguage_local, None)

        return sourcelanguage_local

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

    acronym = models.CharField(_("Acronym"), max_length=25, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ThematicAreaLocal.objects.filter(thematic_area=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "thematicarea-{}-{}".format(lang_code, self.id)
        thematicarea_name_local = cache.get(cache_id)
        if not thematicarea_name_local:
            translation = ThematicAreaLocal.objects.filter(thematic_area=self.id, language=lang_code)
            if translation:
                thematicarea_name_local = translation[0].name
            else:
                thematicarea_name_local = self.name

            cache.set(cache_id, thematicarea_name_local, None)

        return thematicarea_name_local


class ThematicAreaLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    thematic_area = models.ForeignKey(ThematicArea, verbose_name=_("Thematic area"))
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)


# Relation resource -- thematic areas/ Field lis type (302)
class ResourceThematic(Generic, AuditLog):
    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
    )

    class Meta:
        verbose_name = _("Thematic area")
        verbose_name_plural = _("Thematic areas")

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='thematics')
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    thematic_area = models.ForeignKey(ThematicArea, related_name='+')
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, default=PENDING, blank=True)

    def __unicode__(self):
        return self.thematic_area.name


# DeCS descriptors table
class Descriptor(Generic, AuditLog):
    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
    )

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='descriptors')
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    text = models.CharField(_('Descriptor'), max_length=255, blank=True)
    code = models.CharField(_('Code'), max_length=50, blank=True)
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, default=PENDING)
    primary = models.BooleanField(_('Primary?'), default=False)

    def __unicode__(self):
        return self.text


# Keywords table
class Keyword(Generic, AuditLog):
    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
    )

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='keywords')
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    text = models.CharField(_('Text'), max_length=255, blank=True)
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, default=PENDING)
    user_recomendation = models.BooleanField(_('User recomendation?'), default=False)

    def __unicode__(self):
        return self.text


# Main table
class Resource(Generic, AuditLog):

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    # status (399)
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)
    # title (311)
    title = models.CharField(_('Title'), max_length=510, blank=False, help_text=_("Transcribe as it appears on the internet resource. If there is no title, provide a brief, simple but explanatory title"))
    # link (351)
    link = models.TextField(_('Link'), blank=False)
    # originator (313)
    originator = models.TextField(_('Originator'), blank=False, help_text=_("Institutional or personnel name of the responsible for the existence of the internet resource. Ex. Brazilian Society for Dental Research"))
    # originator_location (314)
    originator_location = models.ManyToManyField(Country, verbose_name=_('Originator location'), blank=False)
    # author (315)
    author = models.TextField(_('Authors'), blank=True, help_text=_("Enter one per line. Only filled if different from the originator of the resource"))
    # language of resource (317)
    source_language = models.ManyToManyField(SourceLanguage, verbose_name=_("Source language"), blank=False)
    # source type (318)
    source_type = models.ManyToManyField(SourceType, verbose_name=_("Source type"), blank=False)
    # abstract (319)
    abstract = models.TextField(_("Abstract"), blank=False, help_text=_("Include information on the content and operation of the internet resource"))
    # time period (341)
    time_period_textual = models.CharField(_('Temporal range'), max_length=255, blank=True)
    # objective (361)
    objective = models.TextField(_('Objective'), blank=True)
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    # relations
    error_reports = GenericRelation(ErrorReport)
    thematics = GenericRelation(ResourceThematic)
    descriptors = GenericRelation(Descriptor)

    def get_fields(self):
        return [(field.verbose_name, field.value_to_string(self)) for field in Resource._meta.fields]

    def __unicode__(self):
        return unicode(self.title)
