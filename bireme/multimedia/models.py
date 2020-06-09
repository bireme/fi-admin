#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
from django.core.cache import cache

from utils.models import Generic, Country
from main.choices import LANGUAGES_CHOICES

from django.contrib.contenttypes.generic import GenericRelation
from log.models import AuditLog

from main.models import SourceLanguage, ResourceThematic

# Media Type model
class MediaType(Generic):

    class Meta:
        verbose_name = _("Media type")
        verbose_name_plural = _("Media types")

    acronym = models.CharField(_("Acronym"), max_length=25, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = MediaTypeLocal.objects.filter(media_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "multimedia_mediatype-{}-{}".format(lang_code, self.id)
        mediatype_local = cache.get(cache_id)
        if not mediatype_local:
            translation = MediaTypeLocal.objects.filter(media_type=self.id, language=lang_code)
            if translation:
                mediatype_local = translation[0].name
            else:
                mediatype_local = self.name

            cache.set(cache_id, mediatype_local, None)

        return mediatype_local

class MediaTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    media_type = models.ForeignKey(MediaType, verbose_name=_("Media type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# Collection model
class MediaCollection(Generic):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    date = models.DateField(_('Date'), help_text='Format: DD/MM/YYYY', null=True, blank=True)
    city = models.CharField(_("City"), max_length=255, blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), null=True, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES, blank=True)

    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __unicode__(self):
        return self.name


class MediaCollectionLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    media_collection = models.ForeignKey(MediaCollection, verbose_name=_("Collection"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)


# Media model
class Media(Generic, AuditLog):

    class Meta:
        verbose_name = _("Media")
        verbose_name_plural = _("Medias")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)
    media_type = models.ForeignKey(MediaType, verbose_name=_("Media type"), blank=False)
    media_collection = models.ForeignKey(MediaCollection, verbose_name=_("Collection"), null=True, blank=True)
    title = models.CharField(_('Original title'), max_length=455, blank=False)
    title_translated = models.CharField(_('Translated title'), max_length=455, blank=True)
    link = models.URLField(_('Link'), max_length=255, blank=False)
    description = models.TextField(_("Description"), blank=True)
    authors = models.TextField(_('Authors'), blank=True, help_text=_("Enter one per line"))
    contributors = models.TextField(_('Contributors'), blank=True, help_text=_("Enter one per line"))
    language = models.ManyToManyField(SourceLanguage, verbose_name=_("language"), blank=True)
    item_extension = models.CharField(_('Item extension'), max_length=255, blank=True)
    other_physical_details = models.CharField(_('Other physical details'), max_length=255, blank=True)
    dimension = models.CharField(_('Dimension'), max_length=255, blank=True)
    content_notes = models.TextField(_("Content notes"), blank=True)
    version_notes = models.TextField(_("Version notes"), blank=True)
    related_links = models.TextField(_('Related links'), blank=True, help_text=_("Enter one per line"))
    publisher = models.CharField(_('Publisher'), max_length=255, blank=True)
    publication_date = models.DateField(_('Publication date'), help_text='Format: DD/MM/YYYY', null=True, blank=True)

    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    # relations
    thematics = GenericRelation(ResourceThematic)

    def __unicode__(self):
        return self.title
