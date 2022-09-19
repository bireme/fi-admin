# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from .models_thesaurus import Thesaurus
from .models_qualifiers import *

from utils.models import Generic
from log.models import AuditLog

from thesaurus.choices import *

from multiselectfield import MultiSelectField



class IdentifierDesc(Generic, AuditLog):

    class Meta:
        verbose_name = _("Descriptor")
        verbose_name_plural = _("Descriptors")
        ordering = ('decs_code',)

    thesaurus = models.ForeignKey(Thesaurus, null=True, blank=False, default=None, on_delete=models.PROTECT)

    # DescriptorClass
    descriptor_class = models.CharField(_("Descriptor class"), choices=DESCRIPTOR_CLASS_CODE, max_length=2, blank=True)

    # MESH Descriptor Unique Identifier
    descriptor_ui = models.CharField(_("Transport UI"), max_length=250, blank=True)

    # BIREME Descriptor Unique Identifier
    # decs_code = models.CharField(_("DeCS Descriptor UI"), max_length=250, blank=True, unique=True) # Apos load habilitar esse
    decs_code = models.CharField(_("Thesaurus UI"), max_length=250, blank=True)

    # External Descriptor Unique Identifier
    external_code = models.CharField(_("External Descriptor UI"), max_length=250, blank=True)

    # NLMClassificationNumber
    nlm_class_number = models.CharField(_("NLM classification number"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateRevised
    date_revised =  models.DateField(_("Date revised"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateEstablished
    date_established = models.DateField(_("Date established"), help_text='DD/MM/YYYY', blank=True, null=True)

    abbreviation = models.ManyToManyField(IdentifierQualif, verbose_name='Abbreviation', blank=True)

    def __str__(self):
        lang_code = get_language()
        concepts_of_register = IdentifierConceptListDesc.objects.filter(identifier_id=self.id).values('id').first()
        if concepts_of_register:
            id_concept = concepts_of_register.get('id')
            # Verify if exist term with published status
            has_term = TermListDesc.objects.filter(identifier_concept_id=id_concept, status='1', concept_preferred_term='Y', record_preferred_term='Y')
            if len(has_term) > 0:
                # Verify if exist tradution for the interface choiced
                translation = TermListDesc.objects.filter(identifier_concept_id=id_concept, status='1', language_code=lang_code, concept_preferred_term='Y', record_preferred_term='Y').first()
                if translation:
                    treatment = translation.term_string.replace('/','')
                    return '%s' % treatment
                else:
                    translation = TermListDesc.objects.filter(identifier_concept_id=id_concept, status='1', language_code='en', concept_preferred_term='Y', record_preferred_term='Y').first()
                    if translation:
                        treatment = translation.term_string.replace('/','')
                        return '%s' % treatment
            return '%s' % (self.id)
        else:
            return '%s' % (self.id)



# Description
class DescriptionDesc(models.Model, AuditLog):
# class DescriptionDesc(models.Model):

    class Meta:
        verbose_name = _("Description")
        verbose_name_plural = _("Descriptions")
        unique_together = ('identifier','language_code')

    identifier = models.ForeignKey(IdentifierDesc, related_name="descriptiondesc", null=True, on_delete=models.PROTECT)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # Annotation
    annotation = models.TextField(_("Annotation"), max_length=1500, blank=True)

    # HistoryNote
    history_note = models.TextField(_("History note"), max_length=1500, blank=True)

    # OnlineNote
    online_note = models.TextField(_("Online note"), max_length=1500, blank=True)

    # PublicMeSHNote
    public_mesh_note = models.TextField(_("Public MeSH note"), max_length=1500, blank=True)

    # ConsiderAlso
    consider_also = models.CharField(_("Consider also"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# Tree numbers for descriptors
class TreeNumbersListDesc(models.Model, AuditLog):
# class TreeNumbersListDesc(models.Model):

    class Meta:
        verbose_name = _("Tree number for descriptor")
        verbose_name_plural = _("Tree numbers for descriptors")
        ordering = ('tree_number',)
        unique_together = ('identifier','tree_number')

    identifier = models.ForeignKey(IdentifierDesc, related_name="dtreenumbers", null=True, on_delete=models.PROTECT)

    # Tree Number
    tree_number = models.CharField(_("Tree number"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# PharmacologicalActionList
class PharmacologicalActionList(models.Model, AuditLog):

    class Meta:
        verbose_name = _("Pharmacological Action List")
        verbose_name_plural = _("Pharmacologicals Action List")

    identifier = models.ForeignKey(IdentifierDesc, related_name="pharmacodesc", blank=True, null=True, on_delete=models.PROTECT)

    # String
    term_string = models.CharField(_("String"), max_length=250, blank=True)

    # MESH Descriptor Unique Identifier
    descriptor_ui = models.CharField(_("Transport UI"), max_length=250, blank=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# SeeRelatedList for descriptors
class SeeRelatedListDesc(models.Model, AuditLog):
# class SeeRelatedListDesc(models.Model):

    class Meta:
        verbose_name = _("See Related List")
        verbose_name_plural = _("See Related List")

    identifier = models.ForeignKey(IdentifierDesc, related_name="relateddesc", blank=True, null=True, on_delete=models.PROTECT)

    # String
    term_string = models.CharField(_("String"), max_length=250, blank=True)

    # MESH Descriptor Unique Identifier
    descriptor_ui = models.CharField(_("Transport UI"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# Previous Indexing List
class PreviousIndexingListDesc(models.Model, AuditLog):
# class PreviousIndexingListDesc(models.Model):

    class Meta:
        verbose_name = _("Previous Indexing")
        verbose_name_plural = _("Previous Indexing")

    identifier = models.ForeignKey(IdentifierDesc, related_name="previousdesc", blank=True, null=True, on_delete=models.PROTECT)

    # PreviousIndexing
    previous_indexing = models.CharField(_("Previous indexing"), max_length=1000, blank=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# Administrative information from old system
class legacyInformationDesc(models.Model):

    class Meta:
        verbose_name = _("Legacy information")
        verbose_name_plural = _("Legacy information")

    identifier = models.ForeignKey(IdentifierDesc, related_name="legacyinformationdesc", blank=True, null=True, on_delete=models.PROTECT)

    # c
    pre_codificado = models.CharField(_("Pre-codificado"), max_length=1, blank=True)

    # d
    desastre = models.CharField(_("Desastre"), max_length=1, blank=True)

    # f
    reforma_saude = models.CharField(_("Reforma Saude"), max_length=1, blank=True)

    # g
    geografico = models.CharField(_("Geografico"), max_length=1, blank=True)

    # h
    mesh = models.CharField(_("MeSH"), max_length=1, blank=True)

    # l
    pt_lilacs = models.CharField(_("PT LILACS"), max_length=1, blank=True)

    # n
    nao_indexavel = models.CharField(_("Nao indexavel"), max_length=1, blank=True)

    # p
    homeopatia = models.CharField(_("Homeopatia"), max_length=1, blank=True)

    # r
    repidisca = models.CharField(_("Repidisca"), max_length=1, blank=True)

    # s
    saude_publica = models.CharField(_("Saude Publica"), max_length=1, blank=True)

    # x
    exploded = models.CharField(_("Exploded"), max_length=1, blank=True)

    # z
    geog_decs = models.CharField(_("Geog DeCS"), max_length=1, blank=True)

    def __str__(self):
        return '%s' % (self.id)



class EntryCombinationListDesc(models.Model, AuditLog):

    class Meta:
        verbose_name = _("Entry combination List")
        verbose_name_plural = _("Entry combinations List")

    identifier = models.ForeignKey(IdentifierDesc, related_name="entrycombinationlistdesc", blank=True, null=True, on_delete=models.PROTECT)

    ecin_qualif = models.CharField(_("Qualifier string"), max_length=250, blank=True)
    ecin_id = models.CharField(_("Identifier"), max_length=250, blank=True)

    ecout_desc = models.CharField(_("Descriptor string"), max_length=250, blank=True)
    ecout_desc_id = models.CharField(_("Identifier"), max_length=250, blank=True)

    ecout_qualif = models.CharField(_("Qualifier string"), max_length=250, blank=True)
    ecout_qualif_id = models.CharField(_("Identifier"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# Identifier ConceptList
# class IdentifierConceptListDesc(Generic, AuditLog):
class IdentifierConceptListDesc(models.Model):

    class Meta:
        verbose_name = _("Concept record")
        verbose_name_plural = _("Concept records")

    identifier = models.ForeignKey(IdentifierDesc, blank=True, null=True, on_delete=models.PROTECT)
    # identifier = models.ForeignKey(IdentifierDesc, related_name="identifierconceptdesc", blank=True, null=True)

    # ConceptUI
    concept_ui = models.CharField(_("Concept unique Identifier"), max_length=50, blank=True)

    # ConceptRelationRelationName (NRW | BRD | REL) #IMPLIED >
    concept_relation_name = models.CharField(_("Relationship"), choices=RELATION_NAME_OPTION, max_length=3, blank=True)

    # PreferredConcept
    preferred_concept = models.CharField(_("Preferred concept"), choices=YN_OPTION, max_length=1, blank=True)

    # CASN1Name
    casn1_name = models.TextField(_("Chemical abstract"), max_length=1000, blank=True)

    # RegistryNumber
    registry_number = models.CharField(_("Registry number from CAS"), max_length=250, blank=True)

    # Historical annotation
    historical_annotation = models.TextField(_("Historical annotation"), max_length=1500, blank=True)

    def __str__(self):
        return '%s' % (self.id)




# ConceptList
# class ConceptListDesc(models.Model, AuditLog):
class ConceptListDesc(models.Model):

    class Meta:
        verbose_name = _("Concept")
        verbose_name_plural = _("Concepts")

    identifier_concept = models.ForeignKey(IdentifierConceptListDesc, related_name="conceptdesc", blank=True, null=True, on_delete=models.PROTECT)


    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # ScopeNote
    scope_note = models.TextField(_("Scope note"), max_length=1500, blank=True)

    # def get_parent(self):
    #     return self.identifier_concept

    def __str__(self):
        return '%s' % (self.id)




# TermList
# class TermListDesc(models.Model, AuditLog):
class TermListDesc(models.Model):

    class Meta:
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")
        # ordering = ('language_code','term_string','concept_preferred_term')

    identifier_concept = models.ForeignKey(IdentifierConceptListDesc, related_name="termdesc", blank=True, null=True, on_delete=models.PROTECT)

    # Adminstration field
    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=-1)

    # TermUI
    term_ui = models.CharField(_("Term unique identifier"), max_length=250, blank=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # String
    term_string = models.CharField(_("String"), max_length=250, blank=False)

    # ConceptPreferredTermYN
    concept_preferred_term = models.CharField(_("Concept preferred term"), choices=YN_OPTION, max_length=1, blank=True)

    # IsPermutedTermYN
    is_permuted_term = models.CharField(_("Is permuted term"), choices=YN_OPTION, max_length=1, blank=True)

    # LexicalTag
    lexical_tag =  models.CharField(_("Lexical categories"), choices=LEXICALTAG_OPTION, max_length=3, blank=True)

    # RecordPreferredTerm
    record_preferred_term = models.CharField(_("Record preferred term"), choices=YN_OPTION, max_length=1, blank=True)

    # EntryVersion
    entry_version = models.CharField(_("Entry version"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)
    # date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', auto_now_add=True, editable=False)

    # DateAltered
    date_altered = models.DateField(_("Date altered"), help_text='DD/MM/YYYY', blank=True, null=True)
    # date_altered = models.DateTimeField(_("Date altered"), help_text='DD/MM/YYYY', auto_now=True, editable=False)

    # Historical annotation
    historical_annotation = models.TextField(_("Historical annotation"), max_length=1500, blank=True)

    term_thesaurus = models.CharField(_("Thesaurus"), max_length=50, blank=True)

    # def get_parent(self):
    #     return self.identifier_concept

    def __str__(self):
        return '%s' % (self.id)


# ThesaurusIDlist
class TheraurusOccurrenceListDesc(models.Model):

    class Meta:
        verbose_name = _("Thesaurus occurrence")
        verbose_name_plural = _("Thesaurus occurrence")

    identifier_term = models.ForeignKey(TermListDesc, related_name="tocurrencedesc", blank=True, null=True, on_delete=models.PROTECT)

    # ThesaurusID
    thesaurus_occurrence = models.CharField(_("Name of a thesaurus where terms occur"), max_length=250, blank=True)

    def __str__(self):
        return '%s' % (self.id)
