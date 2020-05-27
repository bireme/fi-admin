from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.cache import cache

from utils.models import Generic
from utils.fields import MultipleAuxiliaryChoiceField

LANGUAGES_CHOICES = (
    ('en', _('English')),  # default language
    ('pt-br', _('Portuguese')),
    ('es', _('Spanish')),
)


class Database(Generic):

    class Meta:
        verbose_name = "Database"
        verbose_name_plural = "Databases"

    acronym = models.CharField(_('Acronym'), max_length=55)
    name = models.CharField(_('Name'), max_length=255)
    regional_index = models.BooleanField(_('Regional index?'), default=False)
    network_index = MultipleAuxiliaryChoiceField(_('Network index'), blank=True)
    cc_index = models.CharField(_('Cooperative Center index'), max_length=55, blank=True)

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "database-{}-{}".format(lang_code, self.id)
        database_name_local = cache.get(cache_id)
        if not database_name_local:
            translation = DatabaseLocal.objects.filter(database=self.id, language=lang_code)
            if translation:
                database_name_local = translation[0].name
            else:
                database_name_local = self.name

            cache.set(cache_id, database_name_local, None)

        return database_name_local


class DatabaseLocal(models.Model):

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"

    database = models.ForeignKey(Database, verbose_name=_("Database"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES[1:])
    name = models.CharField(_("name"), max_length=255)
