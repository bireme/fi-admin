from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, get_language
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from main import choices

#from datetime import datetime

class Generic(models.Model):

    def __init__(self, *args, **kwargs):
        super(Generic, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    class Meta:
        abstract = True

    created_time = models.DateTimeField(_("created at"), auto_now_add=True, editable=False)
    updated_time = models.DateTimeField(_("updated"), auto_now=True, editable=False, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name="+", editable=False)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name="+", editable=False)

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)


    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])


    def save(self, *args, **kwargs):
        super(Generic, self).save(*args, **kwargs)
        self.__initial = self._dict


class CountryManager(models.Manager):
    def get_query_set(self):
        return (
            super(CountryManager, self)
            .get_query_set()
            .order_by('-LA_Caribbean', 'name')
        )

class Country(Generic):

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    code = models.CharField(_('code'), max_length=55)
    name = models.CharField(_('name'), max_length=255)
    LA_Caribbean = models.BooleanField(_('Latin America & Caribbean region?'), default=False)

    objects = CountryManager()

    def get_translations(self):
        translation_list = ["%s^%s" % ('en', self.name.strip())]
        translation = CountryLocal.objects.filter(country=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = CountryLocal.objects.filter(country=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name

class CountryLocal(models.Model):

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    country = models.ForeignKey(Country, verbose_name=_("country"))
    language = models.CharField(_("language"), max_length=10, choices=choices.LANGUAGES_CHOICES[1:])
    name = models.CharField(_("name"), max_length=255)

# Auxiliar table of codes
class AuxCode(Generic):

    class Meta:
        verbose_name = _("auxiliary code")
        verbose_name_plural = _("auxiliary codes")

    code = models.CharField(_("Code"), max_length=155)
    field = models.CharField(_("Field name"), max_length=50)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    label = models.CharField(_("Label"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.label.strip())]
        translation = AuxCodeLocal.objects.filter(auxcode_id=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.label.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def get_all_labels(self):
        label_list = [self.label]
        label_list.extend([local.label for local in AuxCodeLocal.objects.filter(auxcode_id=self.id)])

        return label_list

    def __unicode__(self):
        lang_code = get_language()
        translation = AuxCodeLocal.objects.filter(auxcode_id=self.id, language=lang_code)
        if translation:
            return translation[0].label
        else:
            return self.label


class AuxCodeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    auxcode = models.ForeignKey(AuxCode, verbose_name=_("Source type"))
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    label = models.CharField(_("Label"), max_length=255)

    def __unicode__(self):
        return self.label
