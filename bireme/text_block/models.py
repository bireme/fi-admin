from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from tinymce.models import HTMLField
from main import choices

class TextBlock(models.Model):

    class Meta:
        verbose_name = _("Text block")
        verbose_name_plural = _("Text blocks")

    title = models.CharField(_("Title"), max_length=155)
    slot = models.CharField(_("Slot"), max_length=30, choices=choices.SLOTS)
    order = models.SmallIntegerField(_("Order"), blank=True, null=True)
    user_profile = models.CharField(_("User profile"), max_length=30, choices=choices.USER_PROFILES, blank=True)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    content = HTMLField(_("Content"))

    def get_title(self):
        lang_code = get_language()
        if lang_code == self.language:
            return self.title
        else:
            translation = TextBlockLocal.objects.filter(text_block=self.id, language=lang_code)
            if translation:
                return translation[0].title
            else:
                return self.title

    def get_content(self):
        lang_code = get_language()
        if lang_code == self.language:
            return self.content
        else:
            translation = TextBlockLocal.objects.filter(text_block=self.id, language=lang_code)
            if translation:
                return translation[0].content
            else:
                return self.content

    def __str__(self):
        return self.title


class TextBlockLocal(models.Model):

    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")

    text_block = models.ForeignKey(TextBlock, verbose_name=_("Text block"), on_delete=models.CASCADE)
    language = models.CharField(_("Language"), max_length=10, choices=choices.LANGUAGES_CHOICES)
    title = models.CharField(_("Title"), max_length=155)
    content = HTMLField(_("Content"))
