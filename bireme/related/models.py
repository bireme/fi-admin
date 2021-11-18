#! coding: utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import ugettext, ugettext_lazy as _, get_language
from django.core.cache import cache
from django.conf import settings

from main.choices import LANGUAGES_CHOICES
from utils.models import Generic
from utils.fields import JSONField
from log.models import AuditLog


class ResearchDataType(Generic):
    class Meta:
        verbose_name = _("Research data type")
        verbose_name_plural = _("Research data types")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ResearchDataTypeLocal.objects.filter(researchdatatype=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "related_researchdatatype-{}-{}".format(lang_code, self.id)
        researchdatatype_local = cache.get(cache_id)
        if not researchdatatype_local:
            translation = ResearchDataTypeLocal.objects.filter(researchdatatype=self.id, language=lang_code)
            if translation:
                researchdatatype_local = translation[0].name
            else:
                researchdatatype_local = self.name

            cache.set(cache_id, researchdatatype_local, None)

        return researchdatatype_local


class ResearchDataTypeLocal(models.Model):
    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    researchdatatype = models.ForeignKey(ResearchDataType, verbose_name=_("Research data type"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


class ResourceType(Generic):
    class Meta:
        verbose_name = _("Resource type")
        verbose_name_plural = _("Resource types")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ResourceTypeLocal.objects.filter(resource=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "related_resourcetype-{}-{}".format(lang_code, self.id)
        resourcetype_local = cache.get(cache_id)
        if not resourcetype_local:
            translation = ResourceTypeLocal.objects.filter(resourcetype=self.id, language=lang_code)
            if translation:
                resourcetype_local = translation[0].name
            else:
                resourcetype_local = self.name

            cache.set(cache_id, resourcetype_local, None)

        return resourcetype_local


class ResourceTypeLocal(models.Model):
    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    resourcetype = models.ForeignKey(ResourceType, verbose_name=_("Resource type"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)



class ResearchData(Generic, AuditLog):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    type = models.ForeignKey(ResearchDataType, verbose_name=_('Type'), on_delete=models.PROTECT)
    title = JSONField(_('Title'), dump_kwargs={'ensure_ascii': False})
    description = JSONField(_('Description'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    link = models.URLField(_('Link'),  max_length=255, blank=False)
    language = models.CharField(_('Language'), max_length=10, choices=LANGUAGES_CHOICES, blank=True)

    def __str__(self):
        return self.title[0]['text']


class Resource(Generic, AuditLog):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    type = models.ForeignKey(ResourceType, verbose_name=_('Type'), on_delete=models.PROTECT)
    title = JSONField(_('Title'), dump_kwargs={'ensure_ascii': False})
    description = JSONField(_('Description'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    link = models.URLField(_('Link'),  max_length=255, blank=False)
    language = models.CharField(_('Language'), max_length=10, choices=LANGUAGES_CHOICES, blank=True)

    def __str__(self):
        return self.title[0]['text']
