#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
from django.core.cache import cache

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
        cache_id = "events_eventtype-{}-{}".format(lang_code, self.id)
        eventtype_local = cache.get(cache_id)
        if not eventtype_local:
            translation = EventTypeLocal.objects.filter(event_type=self.id, language=lang_code)
            if translation:
                eventtype_local = translation[0].name
            else:
                eventtype_local = self.name

            cache.set(cache_id, eventtype_local, None)

        return eventtype_local

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
    not_regional_event = models.BooleanField(_('Do not publish in the regional event directory'), default=False)

    title = models.CharField(_('Title'), max_length=455, blank=False, help_text=_("Enter the full name of the event, as it appears and in the same language. Ex: XIX Congresso Brasileiro de Arritmias Cardiacas. XVII Simposio Nacional do DECS-SBCC"))
    start_date = models.DateField(_('Start date'), help_text='DD/MM/YYYY')
    end_date = models.DateField(_('End date'), help_text='DD/MM/YYYY')

    link = models.URLField(_('Link'), max_length=255, help_text=_("Enter the link of event portal"), blank=True)

    address = models.CharField(_('Address'), max_length=255, blank=True, help_text=_("Enter full address of the local of the event to present it in a Google map"))
    city = models.CharField(_('City'), max_length=125, blank=True)
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)

    event_type = models.ManyToManyField(EventType, verbose_name=_("Event type"), blank=False)
    official_language = models.ManyToManyField('main.SourceLanguage', verbose_name=_("Official languages"), blank=True)

    contact_email = models.EmailField(_('Contact email'), blank=True)
    contact_info = models.TextField(_("Information for contact"), blank=True)
    observations = models.TextField(_("Observations"), help_text=_("Enter information about institutions that organize and/or sponsor the event, deadline for submission of papers, simultaneous translation service, event program, etc."), blank=True)
    target_groups = models.TextField(_("Target groups"), blank=True)

    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    # relations
    error_reports = GenericRelation(ErrorReport)
    thematics = GenericRelation(ResourceThematic)

    def __unicode__(self):
        return self.title
