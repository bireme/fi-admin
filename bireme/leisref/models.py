#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache
from django.db import models

from utils.models import Generic
from main.choices import LANGUAGES_CHOICES
from main.models import SourceLanguage
from log.models import AuditLog
from classification.models import Relationship
from django.template.defaultfilters import date as _date
from utils.validators import valid_min_year

STATUS_CHOICES = (
    (-2, _('Related')),
    (-1, _('Draft')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)


# ActCountryRegion
class ActCountryRegion(Generic):

    class Meta:
        verbose_name = _("Act country/region")
        verbose_name_plural = _("Act country/region")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActCountryRegionLocal.objects.filter(act_region=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_countryregion-{}-{}".format(lang_code, self.id)
        countryregion_local = cache.get(cache_id)
        if not countryregion_local:
            translation = ActCountryRegionLocal.objects.filter(act_region=self.id, language=lang_code)
            if translation:
                countryregion_local = translation[0].name
            else:
                countryregion_local = self.name

            cache.set(cache_id, countryregion_local, None)

        return countryregion_local

class ActCountryRegionLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_region = models.ForeignKey(ActCountryRegion, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActType
class ActType(Generic):

    class Meta:
        verbose_name = _("Act type")
        verbose_name_plural = _("Act types")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ManyToManyField(ActCountryRegion, verbose_name=_("Country/Region"), blank=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActTypeLocal.objects.filter(act_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_acttype-{}-{}".format(lang_code, self.id)
        acttype_local = cache.get(cache_id)
        if not acttype_local:
            translation = ActTypeLocal.objects.filter(act_type=self.id, language=lang_code)
            if translation:
                acttype_local = translation[0].name
            else:
                acttype_local = self.name

            cache.set(cache_id, acttype_local, None)

        return acttype_local

class ActTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_type = models.ForeignKey(ActType, verbose_name=_("Act type"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActScope
class ActScope(Generic):

    class Meta:
        verbose_name = _("Act scope")
        verbose_name_plural = _("Act scopes")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ManyToManyField(ActCountryRegion, verbose_name=_("Country/Region"), blank=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActScopeLocal.objects.filter(act_scope=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actscope-{}-{}".format(lang_code, self.id)
        actscope_local = cache.get(cache_id)
        if not actscope_local:
            translation = ActScopeLocal.objects.filter(act_scope=self.id, language=lang_code)
            if translation:
                actscope_local = translation[0].name
            else:
                actscope_local = self.name

            cache.set(cache_id, actscope_local, None)

        return actscope_local

class ActScopeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_scope = models.ForeignKey(ActScope, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# OrganIssuer
class ActOrganIssuer(Generic):

    class Meta:
        verbose_name = _("Organ issuer")
        verbose_name_plural = _("Organ issuer")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ManyToManyField(ActCountryRegion, verbose_name=_("Country/Region"), blank=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActOrganIssuerLocal.objects.filter(organ_issuer=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actorganissuer-{}-{}".format(lang_code, self.id)
        actorganissuer_local = cache.get(cache_id)
        if not actorganissuer_local:
            translation = ActOrganIssuerLocal.objects.filter(organ_issuer=self.id, language=lang_code)
            if translation:
                actorganissuer_local = translation[0].name
            else:
                actorganissuer_local = self.name

            cache.set(cache_id, actorganissuer_local, None)

        return actorganissuer_local


class ActOrganIssuerLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    organ_issuer = models.ForeignKey(ActOrganIssuer, verbose_name=_("Organ issuer"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActSource
class ActSource(Generic):

    class Meta:
        verbose_name = _("Act source")
        verbose_name_plural = _("Act sources")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Country/Region"), blank=True, null=True, on_delete=models.PROTECT)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActSourceLocal.objects.filter(act_source=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actsource-{}-{}".format(lang_code, self.id)
        actsource_local = cache.get(cache_id)
        if not actsource_local:
            translation = ActSourceLocal.objects.filter(act_source=self.id, language=lang_code)
            if translation:
                actsource_local = translation[0].name
            else:
                actsource_local = self.name

            cache.set(cache_id, actsource_local, None)

        return actsource_local

class ActSourceLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_source = models.ForeignKey(ActSource, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActRelationType
class ActRelationType(Generic):

    class Meta:
        verbose_name = _("Act relation type")
        verbose_name_plural = _("Act relation types")

    name = models.CharField(_("name"), max_length=155)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    label_present = models.CharField(_("Present tense form"), max_length=155)
    label_past = models.CharField(_("Past form"), max_length=155)
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Country/Region"), blank=True, null=True, on_delete=models.PROTECT)

    def get_label_translations(self, field):
        translation_list = ["%s~%s" % (self.language, getattr(self, field))]

        translation = ActRelationTypeLocal.objects.filter(relation_type=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, getattr(trans, field)) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def get_label_present_translations(self):
        return self.get_label_translations('label_present')

    def get_label_past_translations(self):
        return self.get_label_translations('label_past')

    def get_label(self, field):
        lang_code = get_language()
        translation = ActRelationTypeLocal.objects.filter(relation_type=self.id, language=lang_code)
        if translation:
            return getattr(translation[0], field)
        else:
            return getattr(self, field)

    def get_label_present(self):
        return self.get_label('label_present')

    def get_label_past(self):
        return self.get_label('label_past')

    def __str__(self):
        return self.get_label('label_present')

class ActRelationTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    relation_type = models.ForeignKey(ActRelationType, verbose_name=_("Act relation type"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    label_present = models.CharField(_("Present tense form"), max_length=155)
    label_past = models.CharField(_("Past form"), max_length=155)


# ActState
class ActState(Generic):

    class Meta:
        verbose_name = _("Act state")
        verbose_name_plural = _("Act states")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Country/Region"), blank=True, null=True, on_delete=models.PROTECT)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActStateLocal.objects.filter(act_state=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actstate-{}-{}".format(lang_code, self.id)
        actstate_local = cache.get(cache_id)
        if not actstate_local:
            translation = ActStateLocal.objects.filter(act_state=self.id, language=lang_code)
            if translation:
                actstate_local = translation[0].name
            else:
                actstate_local = self.name

            cache.set(cache_id, actstate_local, None)

        return actstate_local


class ActStateLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_state = models.ForeignKey(ActState, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)

# ActCity
class ActCity(Generic):

    class Meta:
        verbose_name = _("Act city")
        verbose_name_plural = _("Act cities")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Country/Region"), blank=True, null=True, on_delete=models.PROTECT)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActCityLocal.objects.filter(act_city=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actcity-{}-{}".format(lang_code, self.id)
        actcity_local = cache.get(cache_id)
        if not actcity_local:
            translation = ActCityLocal.objects.filter(act_city=self.id, language=lang_code)
            if translation:
                actcity_local = translation[0].name
            else:
                actcity_local = self.name

            cache.set(cache_id, actcity_local, None)

        return actcity_local


class ActCityLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_city = models.ForeignKey(ActCity, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# ActCollection
class ActCollection(Generic):

    class Meta:
        verbose_name = _("Act collection")
        verbose_name_plural = _("Act collections")

    name = models.CharField(_("Name"), max_length=255)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Country/Region"), blank=True, null=True, on_delete=models.PROTECT)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = ActCollectionLocal.objects.filter(act_collection=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_actcollection-{}-{}".format(lang_code, self.id)
        actcollection_local = cache.get(cache_id)
        if not actcollection_local:
            translation = ActCollectionLocal.objects.filter(act_collection=self.id, language=lang_code)
            if translation:
                actcollection_local = translation[0].name
            else:
                actcollection_local = self.name

            cache.set(cache_id, actcollection_local, None)

        return actcollection_local


class ActCollectionLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    act_collection = models.ForeignKey(ActCollection, on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# Indexed Database
class Database(Generic):

    class Meta:
        verbose_name = "Database"
        verbose_name_plural = "Databases"

    acronym = models.CharField(_('Acronym'), max_length=55)
    name = models.CharField(_('Name'), max_length=255)

    def __str__(self):
        lang_code = get_language()
        cache_id = "leisref_database-{}-{}".format(lang_code, self.id)
        database_local = cache.get(cache_id)
        if not database_local:
            translation = DatabaseLocal.objects.filter(database=self.id, language=lang_code)
            if translation:
                database_local = translation[0].name
            else:
                database_local = self.name

            cache.set(cache_id, database_local, None)

        return database_local


class DatabaseLocal(models.Model):

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    database = models.ForeignKey(Database, verbose_name=_("Database"), on_delete=models.CASCADE)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES[1:])
    name = models.CharField(_("name"), max_length=255)


# ActReference
class Act(Generic, AuditLog):
    class Meta:
        verbose_name = _("Act reference")
        verbose_name_plural = _("Act references")

    status = models.SmallIntegerField(_("Status"), choices=STATUS_CHOICES, null=True, default=-1)
    # país/região do alcance do ato
    scope_region = models.ForeignKey(ActCountryRegion, verbose_name=_("Act country/region"), on_delete=models.PROTECT)
    # tipo do ato
    act_type = models.ForeignKey(ActType, verbose_name=_("Act type"), on_delete=models.PROTECT)
    # lei revisada
    reviewed = models.BooleanField(_('Reviewed?'), default=False)
    # número do ato
    act_number = models.CharField(_("Act number"), max_length=125, blank=True)
    # título do ato
    title = models.CharField(_("Title"), max_length=255, blank=True)
    # denominação do ato
    denomination = models.CharField(_("Denomination"), max_length=255, blank=True)
    # base de dados
    indexed_database = models.ManyToManyField(Database, verbose_name=_("Indexed in"), blank=True)
    # collection
    act_collection = models.ManyToManyField(ActCollection, verbose_name=_("Collection"), blank=True)
    # alcance do ato
    scope = models.ForeignKey(ActScope, verbose_name=_("Act scope"), blank=True, null=True, on_delete=models.PROTECT)
    # estado do alcance do ato
    scope_state = models.ForeignKey(ActState, verbose_name=_("Act scope state"), blank=True, null=True, on_delete=models.PROTECT)
    # cidade do alcance do ato
    scope_city = models.ForeignKey(ActCity, verbose_name=_("Act scope city"), blank=True, null=True, on_delete=models.PROTECT)
    # grupo geográfico do ato
    scope_geo_group = models.CharField(_("Act scope geographic group"), max_length=125, blank=True)
    # nome da fonte
    source_name = models.ForeignKey(ActSource, verbose_name=_("Source name"), blank=True, null=True, on_delete=models.PROTECT)
    # volume
    volumen = models.CharField(_("Volumen"), max_length=125, blank=True)
    # número do fascículo
    fascicle_number = models.CharField(_("Fascicle"), max_length=125, blank=True)
    # paginação
    pages = models.CharField(_("Pages"), max_length=125, blank=True)
    # data de emissão
    issue_date = models.DateField(_("Issue date"), help_text='DD/MM/YYYY',
                                  validators=[valid_min_year], blank=True, null=True)
    # data de publicação
    publication_date = models.DateField(_("Publication date"), help_text='DD/MM/YYYY',
                                        validators=[valid_min_year], blank=True, null=True)
    # orgão emissor do ato (OLD)
    organ_issuer = models.ForeignKey(ActOrganIssuer, verbose_name=_("Organ issuer"), blank=True, null=True,
                                     on_delete=models.PROTECT, related_name='old_organ_issuer')
    # orgão emissor do ato
    issuer_organ = models.ManyToManyField(ActOrganIssuer, verbose_name=_("Organ issuer"), blank=True)
    # idioma do ato
    language = models.ForeignKey(SourceLanguage, verbose_name=_("Language"), blank=True, null=True, on_delete=models.PROTECT)
    # data de vigência do ato
    effectiveness_date = models.DateField(_("Effectiveness date"), help_text='DD/MM/YYYY', blank=True, null=True)
    # vigência do ato
    act_effectiveness = models.CharField(_("Act effectiveness"), max_length=255, blank=True)
    # ementa oficial
    official_ementa = models.TextField(_("Official ementa"), blank=True)
    # ementa não-oficial
    unofficial_ementa = models.TextField(_("Unofficial ementa"), blank=True)
    # observações
    notes = models.TextField(_("Notes"), blank=True)
    # instituição como tema
    institution_as_subject = models.TextField(_("Institution as subject"), blank=True)
    # descritores não autorizados
    local_descriptors = models.TextField(_("Local descriptors"), blank=True)
    # descritores não autorizados
    local_geo_descriptors = models.TextField(_("Local geographic descriptors"), blank=True)
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    # classification
    collection = GenericRelation(Relationship)


    def status_label(self):
        status_dict = dict(STATUS_CHOICES)
        return status_dict.get(self.status)

    def __str__(self):
        if self.title:
            act_title = self.title
        else:
            if self.issue_date:
                act_date = _date(self.issue_date, "d \d\e F \d\e Y")
                act_title = u"{0} Nº {1} - {2}".format(self.act_type, self.act_number, act_date)
            else:
                act_title = u"{0} Nº {1}".format(self.act_type, self.act_number)

        return act_title


# ActRelationship
class ActRelationship(Generic):

    class Meta:
        verbose_name = _("Act Relationship")
        verbose_name_plural = _("Act Relationships")

    # field used in django one to one relationship
    act_related = models.ForeignKey(Act, related_name='related', null=True, on_delete=models.PROTECT)
    # relatonship type
    relation_type = models.ForeignKey(ActRelationType, blank=False, on_delete=models.PROTECT)
    # field to inform a act already present in database
    act_referred = models.ForeignKey(Act, verbose_name=_("Act related"), related_name="referred", null=True, on_delete=models.PROTECT)
    act_apparatus = models.CharField(_("Apparatus"), max_length=125, blank=True)
    order = models.PositiveSmallIntegerField(_("order"), default=0)


# ActURL
class ActURL(Generic):

    class Meta:
        verbose_name = _("Act URL")
        verbose_name_plural = _("Act URLs")

    act = models.ForeignKey(Act, null=True, on_delete=models.PROTECT)
    url = models.URLField(_("URL"), max_length=300)
    language = models.CharField(_("Language"), max_length=10, blank=True)

# Act Alternative ID
class ActAlternateID(models.Model):

    class Meta:
        verbose_name = _("Act Alternate ID")
        verbose_name_plural = _("Act Alternate ID's")

    act = models.ForeignKey(Act, verbose_name=_("Act"), blank=False, on_delete=models.PROTECT)
    alternate_id = models.CharField(_('Alternate id'), max_length=55, blank=False)
