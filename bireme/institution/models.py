#! coding: utf-8
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models

from main.choices import LANGUAGES_CHOICES
from utils.models import Generic, Country
from log.models import AuditLog

STATUS_CHOICES = (
    (-1, _('Draft')),
    (1, _('Published')),
    (2, _('Refused')),
    (3, _('Deleted')),
)

# Institution Type
class Type(Generic):

    class Meta:
        verbose_name = _("Institution type")
        verbose_name_plural = _("Institution types")

    name = models.CharField(_("Name"), max_length=155)
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)

    def get_translations(self):
        translation_list = ["%s^%s" % (self.language, self.name.strip())]
        translation = TypeLocal.objects.filter(type=self.id)
        if translation:
            other_languages = ["%s^%s" % (trans.language, trans.name.strip()) for trans in translation]
            translation_list.extend(other_languages)

        return translation_list

    def __unicode__(self):
        lang_code = get_language()
        translation = TypeLocal.objects.filter(type=self.id, language=lang_code)
        if translation:
            return translation[0].name
        else:
            return self.name


class TypeLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    type = models.ForeignKey(Type, verbose_name=_("Type"))
    language = models.CharField(_("Language"), max_length=10, choices=LANGUAGES_CHOICES)
    name = models.CharField(_("Name"), max_length=155)



# Institution
class Institution(Generic, AuditLog):
    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")

    status = models.SmallIntegerField(_("Status"), choices=STATUS_CHOICES, null=True, default=-1)
    type = models.ForeignKey(Type, verbose_name=_("Type"))
    name = models.CharField(_("Name"), max_length=254, blank=True)
    acronym = models.CharField(_("Acronym"), max_length=55, blank=True)
    cc_code = models.CharField(_('Center code'), max_length=55, blank=True)
    country = models.ForeignKey(Country, verbose_name=_("Country"))
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=155, blank=True)
    state = models.CharField(_("State"), max_length=155, blank=True)
    zipcode = models.CharField(_("Zip code"), max_length=75, blank=True)
    mailbox = models.CharField(_("Mailbox"), max_length=75, blank=True)
    # responsible cooperative center
    cooperative_center_code = models.CharField(_('Cooperative center'), max_length=55, blank=True)

    def __unicode__(self):
        return self.name

    def status_label(self):
        status_dict = dict(STATUS_CHOICES)
        return status_dict.get(self.status)

# Contact phone
class ContactPhone(models.Model):
    PHONE_CHOICES = (
        ('main', _('Main')),
        ('extension', _('Extension')),
        ('fax', _('Fax')),
    )

    class Meta:
        verbose_name = _("Contact phone")
        verbose_name_plural = _("Contact phones")

    institution = models.ForeignKey(Institution, null=True)
    phone_type = models.CharField(_("Type"), max_length=75, choices=PHONE_CHOICES)
    phone_name = models.CharField(_("Name"), max_length=85)
    country_code = models.CharField(_("Country code"), max_length=4)
    phone_number = models.CharField(_("Number"), max_length=55)


# Contact emails
class ContactEmail(models.Model):
    EMAIL_CHOICES = (
        ('main', _('Main')),
        ('other', _('Other')),
    )

    class Meta:
        verbose_name = _("Contact email")
        verbose_name_plural = _("Contact emails")

    institution = models.ForeignKey(Institution, null=True)
    email_type = models.CharField(_("Type"), max_length=75, choices=EMAIL_CHOICES)
    email_name = models.CharField(_("Name"), max_length=85)
    email = models.EmailField(_("Email"), max_length=155)

# Contact person
class ContactPerson(models.Model):
    PREFIX_CHOICES = (
        ('Mr.', _('Mr.')),
        ('Mrs.', _('Mrs.')),
        ('Dr.', _('Dr.')),
    )

    class Meta:
        verbose_name = _("Contact person")
        verbose_name_plural = _("Contact persons")

    institution = models.ForeignKey(Institution, null=True)
    prefix = models.CharField(_("Prefix"), max_length=45, choices=PREFIX_CHOICES)
    name = models.CharField(_("Name"), max_length=155)
    job_title = models.CharField(_("Job title"), max_length=155)


# Institution URL
class URL(models.Model):
    URL_CHOICES = (
        ('main', _('Main')),
        ('other', _('Other')),
    )

    class Meta:
        verbose_name = _("URL")
        verbose_name_plural = _("URLs")

    institution = models.ForeignKey(Institution, null=True)
    url_type = models.CharField(_("Type"), max_length=75, choices=URL_CHOICES)
    url = models.URLField(_("URL"), max_length=300)
