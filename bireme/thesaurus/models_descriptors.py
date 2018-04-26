# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
from utils.models import Generic, Country
from django.contrib.contenttypes.generic import GenericRelation
from main.models import SourceLanguage
from choices import *

from multiselectfield import MultiSelectField

from .models_thesaurus import Thesaurus
from .models_qualifiers import *


# thesaurus fields
class IdentifierDesc(models.Model):

    class Meta:
        verbose_name = _("Descriptor")
        verbose_name_plural = _("Descriptors")
        ordering = ('decs_code',)

    active = models.BooleanField(_("Enabled"), default=False, help_text=_("Check to set it to active"))

    thesaurus = models.ForeignKey(Thesaurus, null=True, blank=False, default=None)

    # DescriptorClass
    descriptor_class = models.CharField(_("Descriptor class"), choices=DESCRIPTOR_CLASS_CODE, max_length=2, blank=True)

    # MESH Descriptor Unique Identifier
    descriptor_ui = models.CharField(_("MESH Descriptor UI"), max_length=250, blank=True, unique=True)

    # BIREME Descriptor Unique Identifier
    decs_code = models.CharField(_("DeCS Descriptor UI"), max_length=250, blank=False, unique=True)

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

    def __unicode__(self):
        return self.descriptor_ui



# Description
class DescriptionDesc(models.Model):

    class Meta:
        verbose_name = _("Description")
        verbose_name_plural = _("Descriptions")
        unique_together = ('language_code','descriptor_name')

    identifier = models.ForeignKey(IdentifierDesc, related_name="descriptors", blank=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=False)

    # DescriptorName
    descriptor_name = models.CharField(_("Term name"), max_length=250, blank=False)

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

    def __unicode__(self):
        return '%s%s%s%s' % (self.descriptor_name,' (',self.language_code,')')



# Tree numbers for descriptors
class TreeNumbersListDesc(models.Model):

    class Meta:
        verbose_name = _("Tree number for descriptor")
        verbose_name_plural = _("Tree numbers for descriptors")
        ordering = ('tree_number',)
        unique_together = ('identifier','tree_number')

    identifier = models.ForeignKey(IdentifierDesc, related_name="dtreenumbers")

    # Tree Number
    tree_number = models.CharField(_("Tree number"), max_length=250, blank=False)

    def __unicode__(self):
        return '%s' % (self.id)



# Previous Indexing List
class PreviousIndexingListDesc(models.Model):

    class Meta:
        verbose_name = _("Previous Indexing")
        verbose_name_plural = _("Previous Indexing")

    identifier = models.ForeignKey(IdentifierDesc, blank=True)

    # PreviousIndexing
    previous_indexing = models.CharField(_("Previous indexing"), max_length=1000, blank=False)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=False)

    def __unicode__(self):
        return '%s' % (self.id)



# ConceptList
class ConceptListDesc(models.Model):

    class Meta:
        verbose_name = _("Concept")
        verbose_name_plural = _("Concepts")
        unique_together = ('identifier','language_code','concept_name')


    identifier = models.ForeignKey(IdentifierDesc, blank=True)

    # concept_relation = models.ForeignKey(ConceptRelationDesc, verbose_name=_("ID da relacao"), blank=True, null=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=False)

    # PreferredConcept
    preferred_concept = models.CharField(_("Preferred concept"), choices=YN_OPTION, max_length=1, blank=True)

    # ConceptUI
    concept_ui = models.CharField(_("Concept unique Identifier"), max_length=50, blank=True)

    # ConceptName
    concept_name = models.CharField(_("Concept name"), max_length=250, blank=False)

    # CASN1Name
    casn1_name = models.TextField(_("Chemical abstract"), max_length=1000, blank=True)

    # RegistryNumber
    registry_number = models.CharField(_("Registry number from CAS"), max_length=250, blank=True)

    # ScopeNote
    scope_note = models.TextField(_("Scope note"), max_length=1500, blank=True)


    def __unicode__(self):
        return '%s' % (self.id)



# class ConceptRelationDesc(models.Model):

#     class Meta:
#         verbose_name = _("Concept")
#         verbose_name_plural = _("Concepts")

#     # relation = models.ForeignKey(ConceptListDesc, blank=True)
#     concept_relation = models.ForeignKey(ConceptListDesc, verbose_name=_("ID da relacao"), blank=True, null=True)

#     # ConceptRelation RelationName
#     relation_name = models.CharField(_("Concept relation"), choices=RELATION_NAME_OPTION, max_length=3, blank=True)

#     # Concept1UI
#     concept1_ui = models.CharField(_("First concept in then Concept relation"), max_length=250, blank=True)

#     # Concept2UI
#     concept2_ui = models.CharField(_("Second concept in then Concept relation"), max_length=250, blank=True)

#     def __unicode__(self):
#         return '%s' % (self.id)



# TermList
class TermListDesc(models.Model):

    class Meta:
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")
        ordering = ('language_code','term_string',)
        unique_together = ('identifier','term_string','language_code')

    identifier = models.ForeignKey(IdentifierDesc, blank=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=False)

    # ConceptPreferredTermYN
    concept_preferred_term = models.CharField(_("Concept preferred term"), choices=YN_OPTION, max_length=1, blank=True)

    # IsPermutedTermYN
    is_permuted_term = models.CharField(_("Is permuted term"), choices=YN_OPTION, max_length=1, blank=True)

    # LexicalTag
    lexical_tag =  models.CharField(_("Lexical categories"), choices=LEXICALTAG_OPTION, max_length=3, blank=True)

    # RecordPreferredTerm
    record_preferred_term = models.CharField(_("Record preferred term"), choices=YN_OPTION, max_length=1, blank=True)

    # TermUI
    term_ui = models.CharField(_("Term unique identifier"), max_length=250, blank=True)

    # String
    term_string = models.CharField(_("String"), max_length=250, blank=False)

    # EntryVersion
    entry_version = models.CharField(_("Entry version"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), blank=True, null=True)

    def __unicode__(self):
        return '%s' % (self.id)
