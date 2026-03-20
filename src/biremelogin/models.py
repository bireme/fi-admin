#! coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
import simplejson

class Profile(models.Model):

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    USER_TYPE_CHOICES = (
        ('basic', _('Basic')),
        ('advanced', _('Advanced')),
    )

    data = models.TextField(_("data"), null=True, blank=True)
    user = models.OneToOneField(User, verbose_name="user", on_delete=models.PROTECT) # allow extension of default django User

    def get_attribute(self, attr):
        data_attribute = ''
        if self.data:
            user_data = simplejson.loads(self.data)
            if user_data:
                data_attribute = user_data.get(attr)

        return data_attribute


# creates automatically and profile
def create_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
post_save.connect(create_profile, sender=User, dispatch_uid="some.unique.string.id")
