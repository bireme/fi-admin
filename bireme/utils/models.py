from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

#from datetime import datetime

class Generic(models.Model):

    def __init__(self, *args, **kwargs):
        super(Generic, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    class Meta:
        abstract = True

    created = models.DateTimeField(_("created at"), default=timezone.now(), editable=False)
    updated = models.DateTimeField(_("updated"), default=timezone.now(), editable=False)
    creator = models.ForeignKey(User, null=True, blank=True, related_name="+", editable=False)
    updater = models.ForeignKey(User, null=True, blank=True, related_name="+", editable=False)

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)


    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    def save(self):
        self.updated = timezone.now()
        super(Generic, self).save()
        self.__initial = self._dict


