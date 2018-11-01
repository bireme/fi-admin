#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from log.models import AuditLog
from main.models import SourceLanguage
from utils.models import Generic
from main.choices import LANGUAGES_CHOICES
from utils.fields import JSONField

STATUS_CHOICES = (
    (-1, _('Draft')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)
STATUS_AGGREGATION = (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4','4'))


# OER Type
class Type(Generic):

    class Meta:
        verbose_name = _("Type")
        verbose_name_plural = _("Types")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = TypeLocal.objects.filter(oer_type=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list


    def __unicode__(self):
        lang_code = get_language()
        translation = TypeLocal.objects.filter(oer_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class TypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    oer_type = models.ForeignKey(Type, verbose_name=_("Type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)

# Rights License
class License(Generic):

    class Meta:
        verbose_name = _("License")
        verbose_name_plural = _("Licenses")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = LicenseLocal.objects.filter(license=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = LicenseLocal.objects.filter(license=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name

class LicenseLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    license = models.ForeignKey(License, verbose_name=_("License"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Course Type
class CourseType(Generic):

    class Meta:
        verbose_name = _("Course type")
        verbose_name_plural = _("Course types")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = CourseTypeLocal.objects.filter(coursetype=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = CourseTypeLocal.objects.filter(coursetype=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class CourseTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    coursetype = models.ForeignKey(CourseType, verbose_name=_("Course type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Technical Resource Type
class TecResourceType(Generic):

    class Meta:
        verbose_name = _("Technical Resource Type")
        verbose_name_plural = _("Technical Resource Types")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = TecResourceTypeLocal.objects.filter(tecresourcetype=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = TecResourceTypeLocal.objects.filter(tecresourcetype=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class TecResourceTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    tecresourcetype = models.ForeignKey(TecResourceType, verbose_name=_("Technical resource type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# OER Format
class Format(Generic):

    class Meta:
        verbose_name = _("Format")
        verbose_name_plural = _("Format")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = FormatLocal.objects.filter(format=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = FormatLocal.objects.filter(format=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class FormatLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    format = models.ForeignKey(Format, verbose_name=_("Format"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)

# OER Interactivity type
class InteractivityType(Generic):

    class Meta:
        verbose_name = _("Interactivity type")
        verbose_name_plural = _("Interactivity types")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def __unicode__(self):
        lang_code = get_language()
        translation = InteractivityTypeLocal.objects.filter(interatype=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class InteractivityTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    interatype = models.ForeignKey(InteractivityType, verbose_name=_("Interactivity type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)

# OER Interactivity level
class InteractivityLevel(Generic):

    class Meta:
        verbose_name = _("Interactivity level")
        verbose_name_plural = _("Interactivity levels")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def __unicode__(self):
        lang_code = get_language()
        translation = InteractivityLevelLocal.objects.filter(interactivitylevel=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class InteractivityLevelLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    interactivitylevel = models.ForeignKey(InteractivityLevel, verbose_name=_("Interactivity level"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)



# OER Difficulty
class Difficulty(Generic):

    class Meta:
        verbose_name = _("Difficulty")
        verbose_name_plural = _("Difficulties")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def __unicode__(self):
        lang_code = get_language()
        translation = DifficultyLocal.objects.filter(difficulty=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class DifficultyLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    difficulty = models.ForeignKey(Difficulty, verbose_name=_("Difficulty"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)

# OER Audience
class Audience(Generic):

    class Meta:
        verbose_name = _("Audience")
        verbose_name_plural = _("Audiences")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = AudienceLocal.objects.filter(audience=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = AudienceLocal.objects.filter(audience=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class AudienceLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    audience = models.ForeignKey(Audience, verbose_name=_("Audience"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Learning Resource Type
class LearningResourceType(Generic):

    class Meta:
        verbose_name = _("Learning resource type")
        verbose_name_plural = _("Learning resource types")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = LearningResourceTypeLocal.objects.filter(coursetype=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = LearningResourceTypeLocal.objects.filter(coursetype=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class LearningResourceTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    coursetype = models.ForeignKey(LearningResourceType, verbose_name=_("Learning resource type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Learning Context
class LearningContext(Generic):

    class Meta:
        verbose_name = _("Learning context")
        verbose_name_plural = _("Learning contexts")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = LearningContextLocal.objects.filter(learningcontext=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = LearningContextLocal.objects.filter(learningcontext=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class LearningContextLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    learningcontext = models.ForeignKey(LearningContext, verbose_name=_("Learning context"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Structure
class Structure(Generic):

    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")

    name = models.CharField(_("Name"), max_length=115)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s~%s" % (self.language, self.name.strip())]
        translation = StructureLocal.objects.filter(structure=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = StructureLocal.objects.filter(structure=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class StructureLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    structure = models.ForeignKey(Structure, verbose_name=_("Structure"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=115)


# Recurso Educacional Aberto
class OER(Generic, AuditLog):
    class Meta:
        verbose_name = _("Open Educational Resource")
        verbose_name_plural = _("Open Educational Resources")

    status = models.SmallIntegerField(_("Status"), choices=STATUS_CHOICES, null=True, default=-1)
    # indica que é um registro CVSP
    CVSP_resource = models.BooleanField(_('CVSP resource'), default=True)
    # título do recurso educacional
    title = models.CharField(_("Title"), max_length=255, blank=False)
    # objetivos
    learning_objectives = models.TextField(_("Learning objectives"), blank=True)
    # descrição
    description = models.TextField(_("Description"), blank=True)
    # responsável pela criação do recurso
    creator = JSONField(_('Creator'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # contribuidores
    contributor = JSONField(_('Contributor'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # tipo do recurso
    type = models.ForeignKey(Type, verbose_name=_("Type"), blank=True, null=True)
    # idioma do recurso
    language = models.ForeignKey(SourceLanguage, verbose_name=_("Language"), blank=True, null=True)
    # tipo do curso
    course_type = models.ManyToManyField(CourseType, verbose_name=_("Course type"), blank=True)
    # estrutura
    structure = models.ForeignKey(Structure, verbose_name=_("Structure"), blank=True, null=True)
    # tipo de recurso técnico
    tec_resource_type = models.ManyToManyField(TecResourceType, verbose_name=_("Technical resource type"), blank=True)
    # formato
    format = models.ManyToManyField(Format, verbose_name=_("Format"), blank=True)
    # tipo de interatividade
    interactivity_type = models.ForeignKey(InteractivityType, verbose_name=_("Interactivity type"), blank=True, null=True)
    # tipo de recurso de aprendizagem
    learning_resource_type = models.ForeignKey(LearningResourceType, verbose_name=_("Learning resource type"), blank=True, null=True)
    # nivel de interatividade
    interactivity_level = models.ForeignKey(InteractivityLevel, verbose_name=_("Interactivity level"), blank=True, null=True)
    # contexto de aprendizagem
    learning_context = models.ForeignKey(LearningContext, verbose_name=_("Learning context"), blank=True, null=True)
    # dificuldade
    difficulty = models.ForeignKey(Difficulty, verbose_name=_("Difficulty"), blank=True, null=True)
    # nível de agregação
    aggregation_level = models.CharField(_("Aggregation Level"), max_length=55, choices=STATUS_AGGREGATION, blank=True)
    # audiência
    audience = models.ManyToManyField(Audience, verbose_name=_("Audience"), blank=True)
    # licença de uso
    license = models.ForeignKey(License, verbose_name=_("Rights license"), blank=True, null=True)
    # publicador
    publisher = models.CharField(_("Publisher"), max_length=155, blank=True)
    # palavras-chave livres
    free_keywords = models.TextField(_('Free keywords'), blank=True)
    # duração do vídeo/audio
    duration = models.CharField(_("Duration"), max_length=155, blank=True)
    # tamanho
    size = models.CharField(_("Size"), max_length=55, blank=True)
    # requisitos técnicos
    technical_requirements = models.CharField(_("Technical requirements"), max_length=155, blank=True)
    # tempo tipico de aprendizagem
    typical_learning_time = models.CharField(_("Typical learning time"), max_length=115, blank=True)
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)
    # identificação do nó CVSP
    cvsp_node = models.CharField(_('CVSP node'), max_length=55, blank=True)

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


# OER types of relationship
class RelationType(Generic):

    class Meta:
        verbose_name = _("Relation type")
        verbose_name_plural = _("Relation types")

    name = models.CharField(_("name"), max_length=155)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    label_active = models.CharField(_("Active form"), max_length=155)
    label_passive = models.CharField(_("Passive form"), max_length=155)

    def get_label_translations(self, field):
        translation_list = ["%s~%s" % (self.language, getattr(self, field))]

        translation = RelationTypeLocal.objects.filter(relation_type=self.id)
        if translation:
            other_languages = ["%s~%s" % (trans.language, getattr(trans, field)) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def get_label_active_translations(self):
        return self.get_label_translations('label_active')

    def get_label_passive_translations(self):
        return self.get_label_translations('label_passive')

    def get_label(self, field):
        lang_code = get_language()
        translation = RelationTypeLocal.objects.filter(relation_type=self.id, language=lang_code)
        if translation:
            return getattr(translation[0], field)
        else:
            return getattr(self, field)

    def get_label_active(self):
        return self.get_label('label_active')

    def get_label_passive(self):
        return self.get_label('label_passive')

    def __unicode__(self):
        return self.get_label('label_active')

class RelationTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    relation_type = models.ForeignKey(RelationType, verbose_name=_("Relation type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    label_active = models.CharField(_("Active form"), max_length=155)
    label_passive = models.CharField(_("Passive form"), max_length=155)


# OER Relationship
class Relationship(Generic):

    class Meta:
        verbose_name = _("Relationship")
        verbose_name_plural = _("Relationships")

    # field used in django one to one relationship
    oer_related = models.ForeignKey(OER, related_name='related', null=True)
    # relatonship type
    relation_type = models.ForeignKey(RelationType, blank=False)
    # field to inform a act already present in database
    oer_referred = models.ForeignKey(OER, verbose_name=_("OER related"), related_name="referred", null=True)
