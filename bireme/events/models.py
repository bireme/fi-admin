#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone

from utils.models import Generic, Country
from main.choices import LANGUAGES_CHOICES
from main.models import ResourceThematic
from error_reporting.models import ErrorReport

from django.contrib.contenttypes.generic import GenericRelation

# Auxiliar table
class EventType(Generic):

    class Meta:
        verbose_name = _("Event type")
        verbose_name_plural = _("Event types")

    acronym = models.CharField(_("Acronym"), max_length=25, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=255)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = EventTypeLocal.objects.filter(event_type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)
        
        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = EventTypeLocal.objects.filter(event_type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class EventTypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    event_type = models.ForeignKey(EventType, verbose_name=_("Event type"))
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("name"), max_length=255)


# Main table
class Event(Generic):

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    STATUS_CHOICES = (
        (0, _('Pending')),
        (1, _('Admitted')),
        (2, _('Refused')),
        (3, _('Deleted')),
    )

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=0)

    title = models.CharField(_('Title'), max_length=455, blank=False)
    start_date = models.DateField(_('Start date'), help_text='DD/MM/YYYY')
    end_date = models.DateField(_('End date'), help_text='DD/MM/YYYY')

    link = models.URLField(_('Link'), blank=True)
   
    address = models.CharField(_('Address'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=125, blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    event_type = models.ManyToManyField(EventType, verbose_name=_("Event type"), blank=False)
    official_language = models.ManyToManyField('main.SourceLanguage', verbose_name=_("Official languages"), blank=True, null=True)

    contact_email = models.EmailField(_('Contact email'), blank=True)
    contact_info = models.TextField(_("Information for contact"), blank=True)
    observations = models.TextField(_("Observations"), blank=True)
    target_groups = models.TextField(_("Target groups"), blank=True)

    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    # relations 
    error_reports = GenericRelation(ErrorReport)
    thematics = GenericRelation(ResourceThematic)

    def __unicode__(self):
        return self.title

