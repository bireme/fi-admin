from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime

LANGUAGES_CHOICES = (
    ('en', 'English'), # default language 
    ('pt-br', 'Brazilian Portuguese'),
    ('es', 'Spanish'),
)

class Generic(models.Model):

    class Meta:
        abstract = True

    created = models.DateTimeField(_("created"), default=datetime.now())
    updated = models.DateTimeField(_("updated"), default=datetime.now())
    creator = models.ForeignKey(User, null=True, blank=True, related_name="+")
    updater = models.ForeignKey(User, null=True, blank=True, related_name="+")

    def save(self):
        self.updated = datetime.now()
        super(Generic, self).save()



class Language(Generic):

    class Meta:
        verbose_name = _("language")
        verbose_name_plural = _("languages")

    name = models.CharField(_("name"), max_length=150)
    code = models.CharField(_("code"), max_length=3)    

    def __unicode__(self):
        return unicode(self.name)

class LanguageLocal(models.Model):

    class Meta:
        verbose_name = _("language translation")
        verbose_name_plural = _("language translations")

    lang = models.ForeignKey(Language, verbose_name=_("language"))
    name = models.CharField(_("name"), max_length=150)
    language = models.CharField(_("language"), max_length=10, choices=LANGUAGES_CHOICES[1:])
