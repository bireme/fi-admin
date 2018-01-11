# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
# from utils.models import Generic, Country
from django.contrib.contenttypes.generic import GenericRelation
from main.models import SourceLanguage

# thesaurus fields
class Thesaurus(models.Model):

    class Meta:
            verbose_name = _("Thesaurus")
            verbose_name_plural = _("Thesaurus")

    thesaurus_name = models.CharField(_("Thesaurus name"), max_length=250, blank=False)

    thesaurus_author = models.CharField(_("Author"), max_length=250, blank=False)

    thesaurus_scope = models.CharField(_("Scope"), max_length=250, blank=False)


    def __unicode__(self):
        return self.thesaurus_name
