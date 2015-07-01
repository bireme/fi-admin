from tastypie.bundle import Bundle
from tastypie.fields import ApiField, CharField
from tastypie.resources import ModelResource

from utils.fields import JSONField


class JSONApiField(ApiField):
    """
    Custom ApiField for dealing with data from custom JSONFields.
    """
    dehydrated_type = 'json'
    help_text = 'JSON structured data.'

    def convert(self, value):
        if value is None:
            return None

        return value


class CustomResource(ModelResource):
    """
    ModelResource subclass that handles looking up models by slugs rather than IDs.
    """
    @classmethod
    def api_field_from_django_field(cls, f, default=CharField):
        """
        Overrides default field handling to support custom JSONField.
        """
        if isinstance(f, JSONField):
            return JSONApiField

        return super(CustomResource, cls).api_field_from_django_field(f, default)
