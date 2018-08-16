# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from .models_thesaurus import Thesaurus

from utils.models import Generic
from log.models import AuditLog

from choices import *

from multiselectfield import MultiSelectField



class IdentifierQualif(Generic):

    class Meta:
        verbose_name = _("Qualifier")
        verbose_name_plural = _("Qualifiers")
        unique_together = ('thesaurus','abbreviation')

    thesaurus = models.ForeignKey(Thesaurus, null=True, blank=False, default=None)

    # MESH Qualifier Unique Identifier
    qualifier_ui = models.CharField(_("MESH Qualifier UI"), max_length=250, blank=True)

    # BIREME Qualifier Unique Identifier
    decs_code = models.CharField(_("DeCS Qualifier UI"), max_length=250, blank=False, unique=True)

    # External Qualifier Unique Identifier
    external_code = models.CharField(_("External Qualifier UI"), max_length=250, blank=True)

    # Abbreviation
    abbreviation = models.CharField(_("Abbreviation"), max_length=4, blank=False)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateRevised
    date_revised =  models.DateField(_("Date revised"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateEstablished
    date_established = models.DateField(_("Date established"), help_text='DD/MM/YYYY', blank=True, null=True)

    def __unicode__(self):
        lang_code = get_language()

        concepts_of_register = IdentifierConceptListQualif.objects.filter(identifier_id=self.id).values('id')
        id_concept = concepts_of_register[0].get('id')
        translation = TermListQualif.objects.filter(identifier_concept_id=id_concept, language_code=lang_code)

        if translation:
            # treatment1 = translation[0].term_string.replace('/','').upper()
            treatment1 = translation[0].term_string.replace('/','')
            # return '%s%s%s' % (self.abbreviation,' - ',treatment1)
            return '%s%s%s%s' % (treatment1,' (',self.abbreviation,')')
        else:
            return '%s%s%s' % ('Description without translation (',self.abbreviation,')')




# Qualifier
class DescriptionQualif(models.Model, AuditLog):
# class DescriptionQualif(models.Model):

    class Meta:
        verbose_name = _("Description of Qualifier")
        verbose_name_plural = _("Descriptions of Qualifier")
        unique_together = ('identifier','language_code')

    identifier = models.ForeignKey(IdentifierQualif, related_name="descriptionqualif", null=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # Annotation
    annotation = models.TextField(_("Annotation"), max_length=1500, blank=True)

    # HistoryNote
    history_note = models.TextField(_("History note"), max_length=1500, blank=True)

    # OnlineNote
    online_note = models.TextField(_("Online note"), max_length=1500, blank=True)

    def get_parent(self):
        return self.identifier

    def __unicode__(self):
        return '%s' % (self.id)
        # return self.qualifier_name
        # return '%s%s%s%s' % (self.qualifier_name,' (',self.language_code,')')



# Tree numbers for qualifiers
class TreeNumbersListQualif(models.Model, AuditLog):
# class TreeNumbersListQualif(models.Model):

    class Meta:
        verbose_name = _("Tree number for qualifier")
        verbose_name_plural = _("Tree numbers for qualifiers")
        ordering = ('tree_number',)
        unique_together = ('identifier','tree_number')

    identifier = models.ForeignKey(IdentifierQualif, related_name="qtreenumbers", null=True)

    # Tree Number
    tree_number = models.CharField(_("Tree number"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __unicode__(self):
        return '%s' % (self.id)




# Identifier ConceptList
# class IdentifierConceptListQualif(models.Model, AuditLog):
class IdentifierConceptListQualif(models.Model):

    class Meta:
        verbose_name = _("Concept record")
        verbose_name_plural = _("Concept records")

    identifier = models.ForeignKey(IdentifierQualif, blank=True, null=True)

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


    def __unicode__(self):
        return '%s' % (self.id)



# ConceptList
# class ConceptListQualif(models.Model, AuditLog):
class ConceptListQualif(models.Model):

    class Meta:
        verbose_name = _("Concept")
        verbose_name_plural = _("Concepts")

    identifier_concept = models.ForeignKey(IdentifierConceptListQualif, related_name="conceptqualif", blank=True, null=True)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # ScopeNote
    scope_note = models.TextField(_("Scope note"), max_length=1500, blank=True)

    # def get_parent(self):
    #     return self.identifier

    def __unicode__(self):
        return '%s' % (self.id)



# TermListQualif
# class TermListQualif(models.Model, AuditLog):
class TermListQualif(models.Model):

    class Meta:
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")
        ordering = ('language_code','term_string','concept_preferred_term')
        # unique_together = ('term_string','language_code','status','date_altered')
        # unique_together = ('term_string','language_code','status')

    identifier_concept = models.ForeignKey(IdentifierConceptListQualif, related_name="termqualif", blank=True, null=True)

    status = models.SmallIntegerField(_('Status'), choices=STATUS_CHOICES, null=True, default=-1)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

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
    term_string = models.CharField(_("String"), max_length=250, blank=True)

    # EntryVersion
    entry_version = models.CharField(_("Entry version"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateAltered
    date_altered = models.DateField(_("Date altered"), help_text='DD/MM/YYYY', blank=True, null=True)

    # Historical annotation
    historical_annotation = models.TextField(_("Historical annotation"), max_length=1500, blank=True)

    # def get_parent(self):
    #     return self.identifier

    def __unicode__(self):
        return '%s' % (self.id)
