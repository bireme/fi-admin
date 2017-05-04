#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from log.models import AuditLog
from main.models import SourceLanguage
from utils.models import Generic
from main.choices import LANGUAGES_CHOICES

STATUS_CHOICES = (
    (-2, _('Related')),
    (-1, _('Draft')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)

# OER Type
class OERType(Generic):

    class Meta:
        verbose_name = _("OER type")
        verbose_name_plural = _("OER types")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActTypeLocal.objects.filter(act_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = OERTypeLocal.objects.filter(oer_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class OERTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    oer_type = models.ForeignKey(OERType, verbose_name=_("Type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# Recurso Educacional Aberto
class OER(Generic, AuditLog):
    class Meta:
        verbose_name = _("OER reference")
        verbose_name_plural = _("OER references")

    status = models.SmallIntegerField(_("Status"), choices=STATUS_CHOICES, null=True, default=-1)
    # título do recurso educacional
    title = models.CharField(_("Title"), max_length=255, blank=False)
    # objetivos
    learning_objectives = models.TextField(_("Learning objectives"), blank=True)
    # descrição
    description = models.TextField(_("Description"), blank=True)
    # tipo do recurso
    oer_type = models.ForeignKey(OERType, verbose_name=_("Type"), blank=True, null=True)
    # idioma do recurso
    language = models.ForeignKey(SourceLanguage, verbose_name=_("Language"), blank=True, null=True)

    def __unicode__(self):
        return self.title


# URL
class OERURL(Generic):

    class Meta:
        verbose_name = _("URL")
        verbose_name_plural = _("URLs")

    oer = models.ForeignKey(OER, null=True)
    url = models.URLField(_("URL"))
    language = models.CharField(_("Language"), max_length=10, blank=True, choices=LANGUAGES_CHOICES)
