from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from tinymce.models import HTMLField
from main import choices


def get_help_fields(source_param):
    help_fields = []

    help_list = Help.objects.filter(source=source_param)
    if help_list:
        help_fields = [h.field for h in help_list]

    return help_fields


# Help tables
class Help(models.Model):

    class Meta:
        verbose_name = _("Help")
        verbose_name_plural = _("Helps")

    source = models.CharField(_("Source"), max_length=25, choices=choices.SOURCE_CHOICES)
    field = models.CharField(_("Field name"), max_length=55)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    help_text = HTMLField(_("Help"))

    def get_help(self):
        lang_code = get_language()
        if lang_code == self.language:
            return self.help_text
        else:
            translation = HelpLocal.objects.filter(help=self.id, language=lang_code)
            if translation:
                return translation[0].help_text
            else:
                return self.help_text



    def __unicode__(self):
        return "%s | %s" % (self.source, self.field)


class HelpLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    help = models.ForeignKey(Help, verbose_name=_("Help"))
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    help_text = HTMLField(_("Help"))
