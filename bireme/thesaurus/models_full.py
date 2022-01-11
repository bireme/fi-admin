# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.db import models

from utils.models import Generic
from log.models import AuditLog

from utils.fields import JSONField


class Descriptor(Generic, AuditLog):

    class Meta:
        verbose_name = _("Full Descriptor")
        verbose_name_plural = _("Full Descriptors")

    thesaurus = models.SmallIntegerField(_("Thesaurus"), null=True, blank=False, default=None)

    # BIREME Descriptor Unique Identifier
    decs_code = models.CharField(_("Thesaurus UI"), max_length=250, blank=True)

    # MESH Descriptor Unique Identifier
    identifier = models.CharField(_("identifier"), max_length=10)

    # Descriptor type
    type = models.CharField(_("type"), max_length=50, blank=True)

    # Boolean status=1 active
    active = models.BooleanField(_('Active'), default=False)

    # label: human-readable version of a resource’s name, in different lang
    label = JSONField(_("Label"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # tree_numbers related to resource
    treeNumber = JSONField(_("Tree Number"), blank=True, null=True)

    # Qualifiers related to resource
    allowableQualifier = JSONField(_("Allowable Qualifier"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # concepts related to resource
    concept = JSONField(_("Concept"), blank=True, null=True)

    # preferredConcept the most prominent representation among the concepts
    preferredConcept = models.CharField(_("Preferred Concept"), max_length=150, blank=True, null=True)

    # preferredTerm the preferred Term for a Descriptor
    preferredTerm = models.CharField(_("Preferred Term"), max_length=150, blank=True, null=True)

    # synonym: human-readable version of a resource’s not preferred terms or concepts, in different lang
    synonym = JSONField(_("Synonym"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # seeAlso: Reference to a Descriptor by a “see related” cross-reference
    seeAlso = JSONField(_("See Related"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # pharmacologicalAction: Reference to a Descriptor describing observed biological activity
    pharmacologicalAction = JSONField(_("Pharmacological Action"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # annotation: Free-text about the use of the Descriptor, in different lang
    annotation = JSONField(_("Annotation"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # considerAlso: Free-text that refers to other terms with related roots, in different lang
    considerAlso = JSONField(_("Consider Also"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # onlineNote: Free-text to direct online searcher to alternate search terms, in different lang
    onlineNote = JSONField(_("Online Note"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # historyNote: Free-text that traces the concept, in different lang
    historyNote = JSONField(_("History Note"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # publicMeSHNote: Free-text about the history of changes, in different lang
    publicMeSHNote = JSONField(_("Public MeSH Note"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # previousIndexing: Free-text used to index the concept before the Descriptor was created, in different lang
    previousIndexing = JSONField(_("Previous Indexing"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # scopeNote: Free-text giving the scope and definition of a PreferredConcept, in different lang
    scopeNote = JSONField(_("Definition"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    entryCombination = JSONField(_("Entry Combination"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # NLMClassificationNumber
    nlmClassificationNumber = models.CharField(_("NLM classification number"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateRevised
    date_revised = models.DateField(_("Date revised"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateEstablished
    date_established = models.DateField(_("Date established"), help_text='DD/MM/YYYY', blank=True, null=True)

    # def __unicode__(self):
    #     return self.descriptor_ui

    def __unicode__(self):
        return '%s' % (self.id)


class Qualifier(Generic, AuditLog):

    class Meta:
        verbose_name = _("Full Qualifier")
        verbose_name_plural = _("Full Qualifiers")

    thesaurus = models.SmallIntegerField(_("Thesaurus"), null=True, blank=False, default=None)

    # BIREME Descriptor Unique Identifier
    decs_code = models.CharField(_("Thesaurus UI"), max_length=250, blank=True)

    # MESH Qualifier Unique Identifier
    identifier = models.CharField(_("identifier"), max_length=10)

    # Boolean status=1 active
    active = models.BooleanField(_('Active'), default=False)

    # Abbreviation
    abbreviation = models.CharField(_("Abbreviation"), max_length=4, blank=False)

    # label: human-readable version of a resource’s name, in different lang
    label = JSONField(_("Label"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # tree_numbers related to resource
    treeNumber = JSONField(_("Tree Number"), blank=True, null=True)

    # concepts related to resource
    concept = JSONField(_("Concept"), blank=True, null=True)

    # preferredConcept the most prominent representation among the concepts
    preferredConcept = models.CharField(_("Preferred Concept"), max_length=150, blank=True, null=True)

    # preferredTerm the preferred Term for a Qualifier
    preferredTerm = models.CharField(_("Preferred Term"), max_length=150, blank=True, null=True)

    # synonym: human-readable version of a resource’s not preferred terms or concepts, in different lang
    synonym = JSONField(_("Synonym"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # annotation: Free-text about the use of the Descriptor, in different lang
    annotation = JSONField(_("Annotation"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # onlineNote: Free-text to direct online searcher to alternate search terms, in different lang
    onlineNote = JSONField(_("Online Note"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # historyNote: Free-text that traces the concept, in different lang
    historyNote = JSONField(_("History Note"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # scopeNote: Free-text giving the scope and definition of a PreferredConcept, in different lang
    scopeNote = JSONField(_("Definition"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateRevised
    date_revised = models.DateField(_("Date revised"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateEstablished
    date_established = models.DateField(_("Date established"), help_text='DD/MM/YYYY', blank=True, null=True)

    # def __unicode__(self):
    #     return self.descriptor_ui

    def __unicode__(self):
        return '%s' % (self.id)

# with mesh rdf data model
class TreeDescriptor(Generic, AuditLog):

    class Meta:
        verbose_name = _("Descriptor Full Tree")
        verbose_name_plural = _("Descriptor Full Trees")

    # Tree Number
    treeNumber = models.CharField(_("Tree number"), max_length=250, blank=True)

    # pk of Descriptor with tree_number
    identifier_id = models.IntegerField(_("identifier_id"), blank=True, null=True)

    # ancestors
    ancestor = JSONField(_("Ancestors"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # preceding_sibling
    preceding_sibling = JSONField(_("Preceding Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Following_sibling
    following_sibling = JSONField(_("Following Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Self
    self_term = JSONField(_("Self"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Descendants
    descendant = JSONField(_("Descendants"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    def __unicode__(self):
        return '%s' % self.treeNumber


# with mesh rdf data model
class TreeQualifier(Generic, AuditLog):

    class Meta:
        verbose_name = _("Qualifier Full Tree")
        verbose_name_plural = _("Qualifier Full Trees")

    # Tree Number
    treeNumber = models.CharField(_("Tree number"), max_length=250, blank=True)

    # pk of Qualifier with tree_number
    identifier_id = models.IntegerField(_("identifier_id"), blank=True, null=True)

    # ancestors
    ancestor = JSONField(_("Ancestors"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # preceding_sibling
    preceding_sibling = JSONField(_("Preceding Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Following_sibling
    following_sibling = JSONField(_("Following Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Self
    self_term = JSONField(_("Self"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Descendants
    descendant = JSONField(_("Descendants"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    def __unicode__(self):
        return '%s' % self.treeNumber


"""
# with ws decs data model
class TreeDescriptor(Generic, AuditLog):

    class Meta:
        verbose_name = _("Descriptor Full Tree")
        verbose_name_plural = _("Descriptor Full Trees")

    # Tree Number
    treeNumber = models.CharField(_("Tree number"), max_length=250, blank=True)

    # pk of Descriptor with tree_number
    identifier_id = models.IntegerField(_("identifier_id"), blank=True, null=True)

    thesaurus = models.SmallIntegerField(_("Thesaurus"), null=True, blank=False, default=None)

    # ancestors
    ancestor = JSONField(_("Ancestors"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # preceding_sibling
    preceding_sibling = JSONField(_("Preceding Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Following_sibling
    following_sibling = JSONField(_("Following Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Self
    self_term = JSONField(_("Self"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Descendants
    descendant = JSONField(_("Descendants"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    def __unicode__(self):
        return '%s' % self.treeNumber
"""
"""
# with ws decs data model
class TreeQualifier(Generic, AuditLog):

    class Meta:
        verbose_name = _("Qualifier Full Tree")
        verbose_name_plural = _("Qualifier Full Trees")

    # Tree Number
    treeNumber = models.CharField(_("Tree number"), max_length=250, blank=True)

    thesaurus = models.SmallIntegerField(_("Thesaurus"), null=True, blank=False, default=None)

    # pk of Qualifier with tree_number
    identifier_id = models.IntegerField(_("identifier_id"), blank=True, null=True)

    # ancestors
    ancestor = JSONField(_("Ancestors"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # preceding_sibling
    preceding_sibling = JSONField(_("Preceding Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Following_sibling
    following_sibling = JSONField(_("Following Siblings"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Self
    self_term = JSONField(_("Self"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    # Descendants
    descendant = JSONField(_("Descendants"), blank=True, null=True, dump_kwargs={'ensure_ascii': False})

    def __unicode__(self):
        return '%s' % self.treeNumber
"""