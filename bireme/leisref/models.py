#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from utils.models import Generic, Country
from main.choices import LANGUAGES_CHOICES
from main.models import SourceLanguage
from log.models import AuditLog

STATUS_CHOICES = (
    (-1, _('Draft')),
    (0, _('Inprocess')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)

# ActType
class ActType(Generic):

    class Meta:
        verbose_name = _("Act type")
        verbose_name_plural = _("Act types")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActTypeLocal.objects.filter(event_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = ActTypeLocal.objects.filter(act_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class ActTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_type = models.ForeignKey(ActType, verbose_name=_("Act type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActScope
class ActScope(Generic):

    class Meta:
        verbose_name = _("Act scope")
        verbose_name_plural = _("Act scopes")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActScopeLocal.objects.filter(event_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = ActScopeLocal.objects.filter(act_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class ActScopeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_type = models.ForeignKey(ActScope, verbose_name=_("Act type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)

# OrganIssuer
class ActOrganIssuer(Generic):

    class Meta:
        verbose_name = _("Organ issuer")
        verbose_name_plural = _("Organ issuer")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActOrganIssuerLocal.objects.filter(event_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = OrganIssuerLocal.objects.filter(act_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class ActOrganIssuerLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    organ_issuer = models.ForeignKey(ActOrganIssuer, verbose_name=_("Organ issuer"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActRelationType
class ActRelationType(Generic):

    class Meta:
        verbose_name = _("Act relation type")
        verbose_name_plural = _("Act relation types")

    name = models.CharField(_("name"), max_length=155)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActRelationTypeLocal.objects.filter(event_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = ActRelationTypeLocal.objects.filter(relation_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class ActRelationTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    relation_type = models.ForeignKey(ActRelationType, verbose_name=_("Act relation type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActRelationship
class ActRelationship(Generic):

    class Meta:
        verbose_name = _("Act Relationship")
        verbose_name_plural = _("Act Relationships")

    # field used in django one to one relationship
    act_related = models.ForeignKey("leisref.Act", related_name='act_related')
    # relatonship type
    relation_type = models.ForeignKey(ActRelationType, blank=False)
    # field to inform a act already present in database
    act_id = models.ForeignKey("leisref.Act", verbose_name=_("Act related"))
    # fields for manual act information
    act_type = models.ForeignKey(ActType, verbose_name=_("Act type"), blank=True, null=True)
    act_number = models.CharField(_("Act number"), max_length=125)
    act_date = models.CharField(_("Date"), max_length=125)
    act_complement = models.CharField(_("Complement"), max_length=125)


# ActReference
class Act(Generic, AuditLog):
    class Meta:
        verbose_name = _("Act reference")
        verbose_name_plural = _("Act references")

    status = models.SmallIntegerField(_("Status"), choices=STATUS_CHOICES, null=True, default=-1)
    # número do ato
    act_number = models.CharField(_("Act number"), max_length=125)
    # título do ato
    title = models.CharField(_("Title"), max_length=255, blank=True)
    # tipo do ato
    act_type = models.ForeignKey(ActType, verbose_name=_("Act type"), blank=True, null=True)
    # denominação do ato
    denomination = models.CharField(_("Denomination"), max_length=125, blank=True)
    # alcance do ato
    scope = models.ForeignKey(ActScope, verbose_name=_("Act scope"), blank=True, null=True)
    # país do alcance do ato
    scope_country = models.ForeignKey(Country, verbose_name=_("Act scope country"), blank=True, null=True)
    # estado do alcance do ato
    scope_state = models.CharField(_("Act scope state"), max_length=125, blank=True)
    # cidade do alcance do ato
    scope_city = models.CharField(_("Act scope city"), max_length=125, blank=True)
    # grupo geográfico do ato
    scope_geo_group = models.CharField(_("Act scope geographic group"), max_length=125, blank=True)
    # nome da fonte
    source_name = models.CharField(_("Source name"), max_length=255, blank=True)
    # volume
    volumen = models.CharField(_("Volumen"), max_length=125, blank=True)
    # número do fascículo
    fascicle_number = models.CharField(_("Fascicle"), max_length=125, blank=True)
    # paginação
    pages = models.CharField(_("Pages"), max_length=125, blank=True)
    # data de emissão
    issue_date = models.CharField(_("Issue date"), max_length=125, blank=True)
    # data de publicação
    publication_date = models.CharField(_("Publication date"), max_length=125, blank=True)
    # republicação do ato
    republication_date = models.CharField(_("Republication date"), max_length=125, blank=True)
    # orgão emissor do ato
    organ_issuer = models.ForeignKey(ActOrganIssuer, verbose_name=_("Organ issuer"), blank=True, null=True)
    # idioma do ato
    language = models.ForeignKey(SourceLanguage, verbose_name=_("Language"), blank=True, null=True)
    # vigência do ato
    act_effectiveness = models.CharField(_("Act effectiveness"), max_length=255, blank=True)
    # ementa oficial
    official_ementa = models.TextField(_("Official ementa"), blank=True)
    # ementa não-oficial
    unofficial_ementa = models.TextField(_("Unofficial ementa"), blank=True)
    # observações
    notes = models.TextField(_("Notes"), blank=True)
