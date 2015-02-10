#-*- coding: utf-8 -*-

from django import forms
import jsonfield


class JSONField(jsonfield.JSONField):
    """JSONField is a generic textfield that serializes/deserializes JSON objects"""

    def formfield(self, **kwargs):
        """Overwrite default formfield method to change html input to hidden and add custom css class"""
        defaults = {'widget': forms.HiddenInput(attrs={'class': "jsonfield"})}
        defaults.update(kwargs)

        return super(JSONField, self).formfield(**defaults)