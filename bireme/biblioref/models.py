#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from utils.fields import JSONField, AuxiliaryChoiceField, MultipleAuxiliaryChoiceField
from utils.models import Generic, Country
from classification.models import Relationship
from log.models import AuditLog

from database.models import Database

STATUS_CHOICES = (
    (-3, _('Migration')),
    (-2, _('Submission')),
    (-1, _('Draft')),
    (0, _('Inprocess')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)


# Bibliographic Record
class Reference(Generic, AuditLog):
    class Meta:
        verbose_name = _("Bibliographic Record")
        verbose_name_plural = _("Bibliographic Records")

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=-1)
    LILACS_indexed = models.BooleanField(_('Validate using LILACS methodology'), default=True)
    BIREME_reviewed = models.BooleanField(_('Reviewed by BIREME?'), default=False)

    # title used for display and search of Reference objects
    reference_title = models.TextField(_('Title'), blank=True)
    # field tag 01
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)
    # field tag 04 (normalized by BIREME - regional indexes)
    indexed_database = models.ManyToManyField(Database, verbose_name=_("Indexed in"), blank=True)
    # field tag 05
    literature_type = models.CharField(_('Literature type'), max_length=10, blank=True)
    # field tag 06
    treatment_level = models.CharField(_('Treatment level'), max_length=10, blank=True)
    # field tag 08
    electronic_address = JSONField(_('Electronic address'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 09
    record_type = AuxiliaryChoiceField(_('Record type'), max_length=10, blank=True)

    # field tag 38
    descriptive_information = JSONField(_('Descriptive information'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 40
    text_language = MultipleAuxiliaryChoiceField(_('Text language'), blank=True)
    # field tag 61
    internal_note = models.TextField(_('Internal note'), blank=True)
    # field tag 64
    publication_date = models.CharField(_('Publication date'), max_length=250, blank=True)
    # field tag 65
    publication_date_normalized = models.CharField(_('Publication normalized date'), max_length=25, blank=True, help_text=_("Format: YYYYMMDD"))
    # field tag 71
    publication_type = MultipleAuxiliaryChoiceField(_('Publication type'), max_length=100, blank=True)
    # field tag 72
    total_number_of_references = models.CharField(_('Total number of references'), max_length=100, blank=True)
    # field tag 74
    time_limits_from = models.CharField(_('Time limits (from)'), max_length=50, blank=True)
    # field tag 75
    time_limits_to = models.CharField(_('Time limits (to)'), max_length=50, blank=True)
    # field tag 76
    check_tags = MultipleAuxiliaryChoiceField(_('Check tags'), max_length=100, blank=True)
    # field tag 78
    person_as_subject = models.TextField(_('Person as subject'), blank=True)
    # field tag 82
    non_decs_region = models.TextField(_('Non-DeCS Region'), blank=True)
    # field tag 83
    abstract = JSONField(_('Abstract'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 84
    transfer_date_to_database = models.CharField(_('Transfer date do database'), max_length=20, blank=True, editable=False)
    # field tag 85
    author_keyword = JSONField(_('Author keyword'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 110
    item_form = AuxiliaryChoiceField(_('Item form'), max_length=10, blank=True)
    # field tag 111
    type_of_computer_file = AuxiliaryChoiceField(_('Type of computer file'), max_length=10, blank=True)
    # field tag 112
    type_of_cartographic_material = AuxiliaryChoiceField(_('Type of cartographic material'), max_length=10, blank=True)
    # field tag 113
    type_of_journal = AuxiliaryChoiceField(_('Type of journal'), max_length=10, blank=True)
    # field tag 114
    type_of_visual_material = AuxiliaryChoiceField(_('Type of visual material'), max_length=10, blank=True)
    # field tag 115
    specific_designation_of_the_material = AuxiliaryChoiceField(_('Specific designation of the material'), max_length=10, blank=True)
    # field tag 500
    general_note = models.TextField(_('General note'), blank=True)
    # field tag 505
    formatted_contents_note = models.TextField(_('Formatted contents note'), blank=True)
    # field tag 530
    additional_physical_form_available_note = models.TextField(_('Additional physical form available note'), blank=True)
    # field tag 533
    reproduction_note = models.TextField(_('Reproduction note'), blank=True)
    # field tag 534
    original_version_note = models.TextField(_('Original version note'), blank=True)
    # field tag 610
    institution_as_subject = models.TextField(_('Institution as subject'), blank=True)
    # field tag 653
    local_descriptors = models.TextField(_('Local descriptors'), blank=True)
    # field tag 899
    software_version = models.CharField(_('Software version'), max_length=50, blank=True, editable=False)
    # control fields
    LILACS_original_id = models.CharField(_('LILACS id'), max_length=8, blank=True, editable=False)
    interoperability_source = models.CharField(_('Interoperability source'), max_length=100, blank=True, editable=False)
    # code of first CC that indexed the record
    indexer_cc_code = models.CharField(_('Indexed by'), max_length=55, blank=True)

    # relations
    collection = GenericRelation(Relationship)

    def __init__(self, *args, **kwargs):
        super(Reference, self).__init__(*args, **kwargs)
        self.__track_fields = ['status']
        for field in self.__track_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def previous_value(self, field):
        orig = '__original_%s' % field
        return getattr(self, orig)

    def __unicode__(self):
        if 'a' in self.treatment_level:
            try:
                ref_child = ReferenceAnalytic.objects.get(id=self.pk)
                if self.literature_type[0] == 'S':
                    ref_title = u"{0}; {1} ({2}), {3} | {4}".format(ref_child.source.title_serial,
                                                                    ref_child.source.volume_serial,
                                                                    ref_child.source.issue_number,
                                                                    ref_child.source.publication_date_normalized[:4],
                                                                    ref_child.title[0]['text'])
                else:
                    ref_title = u"{0} | {1}".format(ref_child.source.title_monographic[0]['text'],
                                                    ref_child.title[0]['text'])
            except:
                # if errors in format dynamic title use raw reference_title field
                ref_title = self.reference_title
        else:
            ref_child = ReferenceSource.objects.get(id=self.pk)
            ref_title = ref_child.__unicode__()

        return ref_title

    def child_class(self):
        """
        Return the child class of the current instance (ex. for use in Content Type)
        """
        if 'a' in self.treatment_level:
            return ReferenceAnalytic
        else:
            return ReferenceSource

    def document_type(self):
        return "%s%s" % (self.literature_type, self.treatment_level)

    def has_duplicates(self):
        has_duplicates = ReferenceDuplicate.objects.filter(reference=self.pk).exists()

        return has_duplicates

    def get_content_type_id(self):
        if 'a' in self.treatment_level:
            ref_class = ReferenceAnalytic
        else:
            ref_class = ReferenceSource

        content_type=ContentType.objects.get_for_model(ref_class).pk

        return content_type

# Source
class ReferenceSource(Reference):

    class Meta:
        verbose_name = _("Bibliographic Record Source")
        verbose_name_plural = _("Bibliographic Records Source")

    # field tags 16
    individual_author_monographic = JSONField(_('Individual author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 17
    corporate_author_monographic = JSONField(_('Corporate author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tags 18
    title_monographic = JSONField(_('Title'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tags 19
    english_title_monographic = models.CharField(_('English translated title'), max_length=400, blank=True)
    # field tag 20
    pages_monographic = models.CharField(_('Pages'), max_length=80, blank=True)
    # field tags 21
    volume_monographic = models.CharField(_('Volume'), max_length=100, blank=True)
    # field tags 23
    individual_author_collection = JSONField(_('Individual author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 24
    corporate_author_collection = JSONField(_('Corporate author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tags 25
    title_collection = JSONField(_('Title'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tags 26
    english_title_collection = models.CharField(_('English translated title'), max_length=250, blank=True)
    # field tags 27
    total_number_of_volumes = models.CharField(_('Total number of volumes'), max_length=10, blank=True)
    # field tags 30
    title_serial = models.TextField(_('Title'), blank=True)
    # field tags 31
    volume_serial = models.CharField(_('Volume'), max_length=100, blank=True)
    # field tags 32
    issue_number = models.CharField(_('Issue number'), max_length=80, blank=True)
    # field tags 35
    issn = models.CharField(_('ISSN'), max_length=40, blank=True)
    # field tag 49
    thesis_dissertation_leader = JSONField(_('Leader'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 50
    thesis_dissertation_institution = models.CharField(_('Institution to which it is submitted'), max_length=300, blank=True)
    # field tag 51
    thesis_dissertation_academic_title = models.CharField(_('Academic title'), max_length=250, blank=True)
    # field tag 62
    publisher = models.TextField(_('Publisher'), blank=True)
    # field tag 63
    edition = models.CharField(_('Edition'), max_length=150, blank=True)
    # field tag 66
    publication_city = models.CharField(_('City of publication'), max_length=100, blank=True)
    # field tag 67
    publication_country = models.ForeignKey(Country, verbose_name=_('Publication country'), blank=True, null=True)
    # field tag 68
    symbol = models.TextField(_('Symbol'), blank=True)
    # field tag 69
    isbn = models.CharField(_('ISBN'), max_length=60, blank=True)
    # field tag 724
    doi_number = models.CharField(_('DOI number'), max_length=150, blank=True)

    def __unicode__(self):
        source_title = ''
        if self.literature_type[0] == 'S':
            source_title = u"{0}; {1} ({2}), {3}".format(self.title_serial,
                                                         self.volume_serial,
                                                         self.issue_number,
                                                         self.publication_date_normalized[:4])
        else:
            if self.title_monographic:
                source_title = u"{0}".format(self.title_monographic[0]['text'])
            elif self.title_collection:
                source_title = u"{0}".format(self.title_collection[0]['text'])

        return source_title

    def has_analytic(self):
        exist_analytic = ReferenceAnalytic.objects.filter(source=self.pk).exists()

        return exist_analytic

    def count_analytic(self):
        count_analytic = ReferenceAnalytic.objects.filter(source=self.pk).count()

        return count_analytic

# Bibliographic Records Analytic
class ReferenceAnalytic(Reference):

    class Meta:
        verbose_name = _("Bibliographic Record Analytic")
        verbose_name_plural = _("Bibliographic Records Analytic")

    source = models.ForeignKey(ReferenceSource, verbose_name=_("Source"), blank=False)
    # field tags 10
    individual_author = JSONField(_('Individual author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 11
    corporate_author = JSONField(_('Corporate author'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 12
    title = JSONField(_('Title'), blank=True, null=True, dump_kwargs={'ensure_ascii': False}, help_text=_("Field mandatory"))
    # field tag 13
    english_translated_title = models.CharField(_('English translated title'), max_length=400, blank=True)
    # field tag 14
    pages = JSONField(_('Pages'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 49
    thesis_dissertation_analytic_leader = JSONField(_('Leader'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 700
    clinical_trial_registry_name = JSONField(_('Clinical trial registry name'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 724
    doi_number = models.CharField(_('DOI number'), max_length=150, blank=True)

    def __unicode__(self):
        if 'a' in self.treatment_level:
            if self.literature_type[0] == 'S':
                ref_title = u"{0}; {1} ({2}), {3} | {4}".format(self.source.title_serial,
                                                                self.source.volume_serial,
                                                                self.source.issue_number,
                                                                self.source.publication_date_normalized[:4],
                                                                self.title[0]['text'])
            else:
                ref_title = u"{0} | {1}".format(self.source.title_monographic[0]['text'],
                                                self.title[0]['text'])
        else:
            ref_title = self.title[0]['text']

        return ref_title


# Bibliographic Record Complement
class ReferenceComplement(models.Model):

    class Meta:
        verbose_name = _("Bibliographic Record Complement")
        verbose_name_plural = _("Bibliographic Records Complement")

    source = models.ForeignKey(Reference, verbose_name=_("Source"), blank=False)

    # field tag 53
    conference_name = models.TextField(_('Conference name'), blank=True)
    # field tag 52
    conference_sponsoring_institution = models.TextField(_('Conference Sponsoring Institution'), blank=True)
    # field tag 54
    conference_date = models.CharField(_('Conference date'), max_length=100, blank=True)
    # field tag 55
    conference_normalized_date = models.CharField(_('Conference normalized date'), max_length=100, blank=True)
    # field tag 56
    conference_city = models.CharField(_('Conference city'), max_length=100, blank=True)
    # field tag 57
    conference_country = models.ForeignKey(Country, verbose_name=_('Conference country'), blank=True, null=True)
    # field tag 59
    project_name = models.CharField(_('Project name'), max_length=500, blank=True)
    # field tag 60
    project_number = models.CharField(_('Project number'), max_length=155, blank=True)
    # field tag 58
    project_sponsoring_institution = models.TextField(_('Project - Sponsoring Institution'), blank=True)


# Bibliographic Record Local information (library tab)
class ReferenceLocal(models.Model):

    class Meta:
        verbose_name = _("Bibliographic Record Local")
        verbose_name_plural = _("Bibliographic Records Local")

    source = models.ForeignKey(Reference, verbose_name=_("Source"), blank=False)
    # field tag 03
    call_number = JSONField(_('Call number'), blank=True, null=True, dump_kwargs={'ensure_ascii': False})
    # field tag 04
    database = models.TextField(_('Database'), blank=True)
    # field tag 07
    inventory_number = models.TextField(_('Inventory number'), blank=True)
    # field tag 61
    internal_note = models.TextField(_('Internal note'), blank=True)
    # field tag 653
    local_descriptors = models.TextField(_('Local descriptors'), blank=True)
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    def __unicode__(self):
        return u"[%s] | %s" % (self.cooperative_center_code, self.source)


# Bibliographic Record Alternative ID
class ReferenceAlternateID(models.Model):

    class Meta:
        verbose_name = _("Bibliographic Record Alternate ID")
        verbose_name_plural = _("Bibliographic Alternate ID's")

    reference = models.ForeignKey(Reference, verbose_name=_("Reference"), blank=False)
    alternate_id = models.CharField(_('Alternate id'), max_length=55, blank=False)


# Bibliographic Record Duplicates (Migration)
class ReferenceDuplicate(models.Model):
    class Meta:
        verbose_name = _("Duplicate Bibliographic Record" )
        verbose_name_plural = _("Duplicate Bibliographic Records")

    reference = models.ForeignKey(Reference, verbose_name=_("Reference"), blank=False)
    metadata_json = models.TextField(_('Metadata JSON'), blank=True)
    indexing_json = models.TextField(_('Indexing JSON'), blank=True)
    complement_json = models.TextField(_('Event/Project JSON'), blank=True)
    library_json = models.TextField(_('Library JSON'), blank=True)
    others_json = models.TextField(_('Other fields JSON'), blank=True)
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)
