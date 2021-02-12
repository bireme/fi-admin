# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from .models_thesaurus import Thesaurus

from utils.models import Generic
from log.models import AuditLog

from thesaurus.choices import *

from multiselectfield import MultiSelectField



class IdentifierQualif(Generic, AuditLog):

    class Meta:
        verbose_name = _("Qualifier")
        verbose_name_plural = _("Qualifiers")
        unique_together = ('thesaurus','abbreviation')

    thesaurus = models.ForeignKey(Thesaurus, null=True, blank=False, default=None, on_delete=models.PROTECT)

    # MESH Qualifier Unique Identifier
    qualifier_ui = models.CharField(_("Transport UI"), max_length=250, blank=True)

    # BIREME Qualifier Unique Identifier
    # decs_code = models.CharField(_("DeCS Qualifier UI"), max_length=250, blank=True, unique=True)
    decs_code = models.CharField(_("Thesaurus UI"), max_length=250, blank=True)

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

    def __str__(self):
        lang_code = get_language()

        concepts_of_register = IdentifierConceptListQualif.objects.filter(identifier_id=self.id).values('id')
        if concepts_of_register:
            id_concept = concepts_of_register[0].get('id')
            # Verify if exist term with published status
            has_term = TermListQualif.objects.filter(identifier_concept_id=id_concept, status='1', concept_preferred_term='Y', record_preferred_term='Y', )
            if len(has_term) > 0:
                # Verifý if exist tradution for the interface choiced
                translation = TermListQualif.objects.filter(identifier_concept_id=id_concept, status='1', language_code=lang_code, concept_preferred_term='Y', record_preferred_term='Y', )
                if translation:
                    # treatment1 = translation[0].term_string.replace('/','').upper()
                    treatment1 = translation[0].term_string.replace('/','')
                    # return '%s%s%s' % (self.abbreviation,' - ',treatment1)
                    return '%s%s%s%s' % (treatment1,' (',self.abbreviation,')')
                else:
                    return '%s%s%s' % ('Description without translation (',self.abbreviation,')')
            return '%s' % ''
        else:
            return '%s' % (self.id)



# Qualifier
class DescriptionQualif(models.Model, AuditLog):
# class DescriptionQualif(models.Model):

    class Meta:
        verbose_name = _("Description of Qualifier")
        verbose_name_plural = _("Descriptions of Qualifier")
        unique_together = ('identifier','language_code')

    identifier = models.ForeignKey(IdentifierQualif, related_name="descriptionqualif", null=True, on_delete=models.PROTECT)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # Annotation
    annotation = models.TextField(_("Annotation"), max_length=1500, blank=True)

    # HistoryNote
    history_note = models.TextField(_("History note"), max_length=1500, blank=True)

    # OnlineNote
    online_note = models.TextField(_("Online note"), max_length=1500, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
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

    identifier = models.ForeignKey(IdentifierQualif, related_name="qtreenumbers", null=True, on_delete=models.PROTECT)

    # Tree Number
    tree_number = models.CharField(_("Tree number"), max_length=250, blank=True)

    def get_parent(self):
        return self.identifier

    def __str__(self):
        return '%s' % (self.id)



# Administrative information from old system
class legacyInformationQualif(models.Model):

    class Meta:
        verbose_name = _("Legacy information")
        verbose_name_plural = _("Legacy information")

    identifier = models.ForeignKey(IdentifierQualif, related_name="legacyinformationqualif", blank=True, null=True, on_delete=models.PROTECT)

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



# Identifier ConceptList
# class IdentifierConceptListQualif(models.Model, AuditLog):
class IdentifierConceptListQualif(models.Model):

    class Meta:
        verbose_name = _("Concept record")
        verbose_name_plural = _("Concept records")

    identifier = models.ForeignKey(IdentifierQualif, blank=True, null=True, on_delete=models.PROTECT)

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
# class ConceptListQualif(models.Model, AuditLog):
class ConceptListQualif(models.Model):

    class Meta:
        verbose_name = _("Concept")
        verbose_name_plural = _("Concepts")

    identifier_concept = models.ForeignKey(IdentifierConceptListQualif, related_name="conceptqualif", blank=True, null=True, on_delete=models.PROTECT)

    language_code = models.CharField(_("Language used for description"), choices=LANGUAGE_CODE_MESH, max_length=10, blank=True)

    # ScopeNote
    scope_note = models.TextField(_("Scope note"), max_length=1500, blank=True)

    # def get_parent(self):
    #     return self.identifier

    def __str__(self):
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

    identifier_concept = models.ForeignKey(IdentifierConceptListQualif, related_name="termqualif", blank=True, null=True, on_delete=models.PROTECT)

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
    term_string = models.CharField(_("String"), max_length=250, blank=False)

    # EntryVersion
    entry_version = models.CharField(_("Entry version"), max_length=250, blank=True)

    # DateCreated
    date_created = models.DateField(_("Date created"), help_text='DD/MM/YYYY', blank=True, null=True)

    # DateAltered
    date_altered = models.DateField(_("Date altered"), help_text='DD/MM/YYYY', blank=True, null=True)

    # Historical annotation
    historical_annotation = models.TextField(_("Historical annotation"), max_length=1500, blank=True)

    term_thesaurus = models.CharField(_("Thesaurus"), max_length=50, blank=True)

    # def get_parent(self):
    #     return self.identifier

    def __str__(self):
        return '%s' % (self.id)
