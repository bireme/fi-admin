#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
from utils.models import Generic, Country
from django.contrib.contenttypes.generic import GenericRelation
from main.models import SourceLanguage
from choices import *

# Title model
class Title(Generic):

    class Meta:
        verbose_name = _("Title")
        verbose_name_plural = _("Titles")

    LOCAL_CODE_CHOICES = (
        ('LOCAL', _('LOCAL')),
    )

    STATUS_CHOICES = (
        ('C', _('Current')),
        ('?', _('Unknown')),
        ('D', _('Suspended or closed')),
    )

    id_number = models.CharField(_('ID number'), max_length=55, blank=False)
    local_code = models.CharField(_('Local code'), max_length=55, choices=LOCAL_CODE_CHOICES, blank=True)
    record_type = models.CharField(_('Record type'), max_length=55, default='KS', blank=False)
    treatment_level = models.CharField(_('Title treatment level'), max_length=55, default='K', blank=False)
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=False)
    national_code = models.CharField(_('National code'), max_length=55, blank=True)
    secs_number = models.CharField(_('SeCS number'), max_length=55, blank=True)
    related_systems = models.TextField(_("Related systems"), blank=True, help_text=_("Enter one per line"))
    status = models.CharField(_('Publish status'), max_length=55, choices=STATUS_CHOICES, blank=False)
    title = models.CharField(_('Title'), max_length=455, blank=False)
    subtitle = models.CharField(_('Subtitle'), max_length=455, blank=True)
    section = models.CharField(_('Section/Part'), max_length=255, blank=True)
    section_title = models.CharField(_('Section/Part title'), max_length=455, blank=True)
    responsibility_mention = models.TextField(_("Responsibility Mention"), blank=True, help_text=_("Enter one per line"))
    shortened_title = models.CharField(_('Shortened title'), max_length=455, blank=False)
    medline_shortened_title = models.CharField(_('MEDLINE shortened title'), max_length=455, blank=True)
    initial_date = models.CharField(_('Initial date'), max_length=255, blank=True)
    initial_volume = models.CharField(_('Initial volume'), max_length=55, blank=True)
    initial_number = models.CharField(_('Initial number'), max_length=55, blank=True)
    final_date = models.CharField(_('Final date'), max_length=255, blank=True)
    final_volume = models.CharField(_('Final volume'), max_length=255, blank=True)
    final_number = models.CharField(_('Final number'), max_length=255, blank=True)
    country = models.ManyToManyField(Country, verbose_name=_('Country'), blank=False)
    state = models.CharField(_('State'), max_length=255, blank=True)
    publication_level = models.CharField(_('Publication level'), max_length=55, choices=PUBLICATION_LEVEL_CHOICES, blank=True)
    title_alphabet = models.CharField(_('Title alphabet'), max_length=55, choices=TITLE_ALPHABET_CHOICES, blank=True)
    text_language = models.ManyToManyField(SourceLanguage, related_name="text_language+", verbose_name=_("Text language"), blank=True)
    abstract_language = models.ManyToManyField(SourceLanguage, related_name="abstract_language+", verbose_name=_("Abstract language"), blank=True)
    frequency = models.CharField(_('Frequency'), max_length=55, choices=FREQUENCY_CHOICES, blank=True)
    issn = models.CharField(_('ISSN'), max_length=255, blank=True)
    coden = models.CharField(_('CODEN'), max_length=255, blank=True)
    medline_code = models.CharField(_('MEDLINE code'), max_length=255, blank=True)
    classification = models.TextField(_("Classification"), blank=True, help_text=_("Enter one per line"))
    thematic_area = models.TextField(_("Thematic area"), blank=True, help_text=_("Enter one per line"))
    user = models.TextField(_("Users"), blank=True, help_text=_("Enter one per line"))
    acquisition_form = models.CharField(_('Acquisition Form'), max_length=55, choices=ACQUISITION_FORM_CHOICES, blank=True)
    acquisition_priority = models.CharField(_('Acquisition priority'), max_length=55, choices=ACQUISITION_PRIORITY_CHOICES, blank=True)
    comercial_editor = models.CharField(_('Comercial editor'), max_length=455, blank=True)
    city = models.CharField(_('City'), max_length=455, blank=True)
    lilacs_index_year = models.CharField(_('Index - Year/Start (LILACS)'), help_text='Format: YYYY', max_length=55, blank=True)
    notes = models.TextField(_("Notes"), blank=True, help_text=_("Enter one per line"))
    bireme_notes = models.TextField(_("BIREME notes"), blank=True, help_text=_("Enter one per line"))
    indexer_cc_code = models.CharField(_('Indexer center code'), max_length=55, blank=True)
    editor_cc_code = models.CharField(_('Editor code'), max_length=55, blank=True)
    creation_date = models.CharField(_('Creation date'), help_text='Format: YYYYMMDD', max_length=55, blank=False)
    last_change_date = models.CharField(_('Last change date'), help_text='Format: YYYYMMDD', max_length=55, blank=True)

    def __unicode__(self):
        return self.title

class OwnerList(Generic):

    class Meta:
        verbose_name = _("Owner List")
        verbose_name_plural = _("Owners List")

    owner = models.CharField(_('Owner'), max_length=455, blank=True)

    def __unicode__(self):
        return self.owner

class OnlineResources(models.Model):

    class Meta:
        verbose_name = _("Online resource")
        verbose_name_plural = _("Online resources")

    title = models.ForeignKey(Title, verbose_name=_("Title"), blank=True, null=True)
    url = models.URLField(_('URL'), max_length=255, blank=True)
    owner = models.ForeignKey(OwnerList, verbose_name=_("Owner"), blank=True, null=True)
    issn_online = models.CharField(_('ISSN online'), max_length=55, blank=True)
    tco = models.BooleanField(_('ONLINE full text'), default=False)
    ndb = models.BooleanField(_('Unavailable for libraries'), default=False)
    pca = models.BooleanField(_('Allows buying articles'), default=False)
    access_type = models.CharField(_('Access type'), max_length=255, choices=ACCESS_TYPE_CHOICES, blank=True)
    access_control = models.CharField(_('Access control'), max_length=255, choices=ACCESS_CONTROL_CHOICES, blank=True)
    initial_period = models.CharField(_('Initial period'), max_length=455, blank=True)
    final_period = models.CharField(_('Final period'), max_length=455, blank=True)
    creation_date = models.CharField(_('Creation date'), help_text='Format: YYYYMMDD', max_length=55, blank=True)
    notes = models.TextField(_("Observations"), blank=True, help_text=_("Enter one per line"))

    def __unicode__(self):
        return self.title.title

class TitleVariance(models.Model):

    class Meta:
        verbose_name = _("Title variance")
        verbose_name_plural = _("Title variances")

    title = models.ForeignKey(Title, verbose_name=_("Original title"), blank=True)
    type = models.CharField(_('Type'), max_length=55, choices=TITLE_VARIANCE_CHOICES, blank=True)
    label = models.CharField(_('Title'), max_length=455, blank=True)
    issn = models.CharField(_('ISSN'), max_length=55, blank=True)
    initial_year = models.CharField(_('Initial year'), help_text='Format: YYYY', max_length=55, blank=True)

    def __unicode__(self):
        return self.label

class BVSSpecialty(models.Model):

    class Meta:
        verbose_name = _("BVS Specialty")
        verbose_name_plural = _("BVS Specialties")

    title = models.ForeignKey(Title, verbose_name=_("Title"), blank=True)
    bvs = models.CharField(_('BVS'), max_length=455, blank=True)
    thematic_area = models.CharField(_('Thematic area'), max_length=55, blank=True)

    def __unicode__(self):
        return self.title.title

class IndexRange(models.Model):

    INDEX_CODE_CHOICES = (
        ('IM', _('Index Medicus')),
        ('IL', _('Index Medicus Latin American')),
        ('EM', _('Excerpta Medica')),
        ('BA', _('Biological abstracts')),
        ('LL', _('LILACS')),
        ('SP', _('Public Health')),
    )

    class Meta:
        verbose_name = _("Index range")
        verbose_name_plural = _("Index range")

    title = models.ForeignKey(Title, verbose_name=_("Title"), blank=True)
    index_code = models.CharField(_('Index source code'), max_length=55, choices=INDEX_CODE_CHOICES, blank=True)
    initial_date = models.CharField(_('Initial date'), max_length=255, blank=True)
    initial_volume = models.CharField(_('Initial volume'), max_length=55, blank=True)
    initial_number = models.CharField(_('Initial number'), max_length=55, blank=True)
    final_date = models.CharField(_('Final date'), max_length=255, blank=True)
    final_volume = models.CharField(_('Final volume'), max_length=255, blank=True)
    final_number = models.CharField(_('Final number'), max_length=255, blank=True)

    def __unicode__(self):
        return self.index_code

class Audit(models.Model):

    class Meta:
        verbose_name = _("Audit")
        verbose_name_plural = _("Audit")

    title = models.ForeignKey(Title, verbose_name=_("Original title"), blank=True)
    type = models.CharField(_('Type'), max_length=55, choices=AUDIT_CHOICES, blank=True)
    label = models.CharField(_('Title'), max_length=455, blank=True)
    issn = models.CharField(_('ISSN'), max_length=55, blank=True)

    def __unicode__(self):
        return self.label
