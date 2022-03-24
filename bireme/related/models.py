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


class LinkedResourceType(Generic):
    class Meta:
        verbose_name = _("Resource type")
        verbose_name_plural = _("Resource types")

    field = models.CharField(_("Field"), max_length=25)
    name = models.CharField(_("Name"), max_length=55)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    order = models.PositiveSmallIntegerField(_("Order"))

    field_passive = models.ForeignKey('self', verbose_name=_("Field passive"), null=True, blank=True, on_delete=models.PROTECT)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = LinkedResourceTypeLocal.objects.filter(resource=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "related_resourcetype-{}-{}".format(lang_code, self.id)
        resourcetype_local = cache.get(cache_id)
        if not resourcetype_local:
            translation = LinkedResourceTypeLocal.objects.filter(type=self.id, language=lang_code)
            if translation:
                resourcetype_local = translation[0].name
            else:
                resourcetype_local = self.name

            cache.set(cache_id, resourcetype_local, None)

        return resourcetype_local


class LinkedResourceTypeLocal(models.Model):
    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    type = models.ForeignKey(LinkedResourceType, verbose_name=_("Resource type"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=55)


class LinkedResearchData(Generic, AuditLog):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    link = models.URLField(_('Link'),  max_length=255, blank=False)
    title = models.CharField(_('Title'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)

    def __str__(self):
        title = self.title if self.title else self.link

        return title

class LinkedResource(Generic, AuditLog):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    type = models.ForeignKey(LinkedResourceType, verbose_name=_('Type'), on_delete=models.PROTECT)
    internal_id = models.CharField(_("FI-ADMIN Reference"), max_length=55, blank=True)
    title = models.CharField(_('Title'), max_length=255, blank=True)
    link = models.URLField(_('Link'),  max_length=255, blank=True)

    def __str__(self):
        title = self.title if self.title else self.link if self.link else self.internal_id

        return title
