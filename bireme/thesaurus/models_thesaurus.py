# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone

from main.models import SourceLanguage

# thesaurus fields
class Thesaurus(models.Model):

    class Meta:
            verbose_name = _("Thesaurus")
            verbose_name_plural = _("Thesaurus")

    thesaurus_name = models.CharField(_("Thesaurus name"), max_length=250, blank=False)

    thesaurus_author = models.CharField(_("Author"), max_length=250, blank=False)

    thesaurus_scope = models.CharField(_("Scope"), max_length=250, blank=False)

    thesaurus_acronym = models.CharField(_("Thesaurus acronym"), max_length=3, blank=True)


    def __unicode__(self):
        return self.thesaurus_name


# Sequential control table of codes for decs_code, descriptor_ui and qualifier_ui uses
class code_controller(models.Model):
    class Meta:
        verbose_name = _("Sequencial control")
        verbose_name_plural = _("Sequencial controls")

    sequential_number = models.CharField(_("Sequential number"), max_length=250, blank=False)

    thesaurus = models.CharField(_("Thesaurus"), max_length=50, blank=True)

    def __unicode__(self):
        return self.id


# TERMs - Sequential control table of codes for term_ui use
class code_controller_term(models.Model):
    class Meta:
        verbose_name = _("Sequencial control")
        verbose_name_plural = _("Sequencial controls")

    sequential_number = models.CharField(_("Sequential number"), max_length=250, blank=False)

    thesaurus = models.CharField(_("Thesaurus"), max_length=50, blank=True)

    def __unicode__(self):
        return self.id