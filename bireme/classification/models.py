#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from django.db import models
from log.models import AuditLog
from utils.models import Generic, Country

from main.choices import LANGUAGES_CHOICES
import os


def attachment_upload(instance, filename):

    fname, dot, extension = filename.rpartition('.')
    slug_filename = "%s.%s" % (slugify(fname), extension)

    upload_path = 'collection/image/%s' % (slug_filename)

    return upload_path

# Community/Collection
class Collection(models.Model, AuditLog):
    TYPE_CHOICES = (
        (0, _('Category')),
        (1, _('Theme')),
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    parent = models.ForeignKey('self', verbose_name=_("Parent"), null=True, blank=True, related_name='children')
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    country = models.ForeignKey(Country, verbose_name=_('Country'), blank=True, null=True)
    name = models.CharField(_("Name"), max_length=155, blank=True)
    slug = models.SlugField(_("Slug"), max_length=155, blank=True)
    description = models.TextField(_("Description"), blank=True)
    image = models.FileField(_("Image"), upload_to=attachment_upload, blank=True)
    community_flag = models.BooleanField(_('Community?'), default=False)
    type = models.SmallIntegerField(_('Collection type'), choices=TYPE_CHOICES, null=True, default=0)
    updated_time = models.DateTimeField(_("Last update"), auto_now=True, editable=False, null=True, blank=True)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = CollectionLocal.objects.filter(collection=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list


    def get_children(self, *args, **kwargs):
        children = Collection.objects.filter(parent=self.id)

        return children

    def get_parents(self):
        parent_list = []
        if self.parent:
            parent_id = self.parent.id
            while parent_id != False:
                collection = Collection.objects.get(pk=parent_id)
                parent_list.append(collection)

                if collection.parent:
                    parent_id = collection.parent.id
                else:
                    parent_id = False
        # reverse list order
        parent_list.reverse()

        return parent_list

    def community_collection_path(self):
        parent_list = [unicode(parent) for parent in self.get_parents()]
        full_list = parent_list + [self.name]
        parent_path = ' / '.join(full_list)

        return parent_path

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)

    def __unicode__(self):
        lang_code = get_language()
        cache_id = "classification_collection-{}-{}".format(lang_code, self.id)
        collection_local = cache.get(cache_id)
        if not collection_local:
            translation = CollectionLocal.objects.filter(collection=self.id, language=lang_code)
            if translation:
                collection_local = translation[0].name
            else:
                collection_local = self.name

            has_children = Collection.objects.filter(parent=self.id).exists()
            if self.country and has_children:
                collection_local = u"{} ({})".format(collection_local, self.country)

            cache.set(cache_id, collection_local, None)

        return collection_local

class CollectionLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    collection = models.ForeignKey(Collection, verbose_name=_("Collection"))
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=155)
    description = models.TextField(_("Description"), blank=True)
    image = models.FileField(_("Image"), upload_to=attachment_upload, blank=True)


# Relationship Object x Collection
class Relationship(models.Model, AuditLog):

    class Meta:
        unique_together = (('object_id', 'content_type', 'collection'),)

    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, related_name='relationship')
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    collection = models.ForeignKey(Collection, verbose_name=_("Collection"))

    updated_time = models.DateTimeField(_("updated"), auto_now=True, editable=False, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name="+", editable=False)

    def save(self, *args, **kwargs):
        super(Relationship, self).save(*args, **kwargs)

        # after save the relationship update last update date of all parents
        parent_list = self.collection.get_parents()
        for parent in parent_list:
            parent.save()


    def __unicode__(self):
        return unicode(self.collection)
