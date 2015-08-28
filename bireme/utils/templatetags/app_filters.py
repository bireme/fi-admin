from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

import json

register = template.Library()

@register.filter
def fieldtype(obj):
    return obj.__class__.__name__


@register.filter()
def log_json_changes(obj):
    log_str = ''
    if obj.change_message:
        data = json.loads(obj.change_message)
        model = obj.content_type.model_class()

        for change in data:
            field_name = model._meta.get_field(change['field_name']).verbose_name.encode('utf-8')
            previous_str = format_jsonfield(change['previous_value'])
            new_str = format_jsonfield(change['new_value'])

            log_str = ('{log_str}<strong>{field}:</strong> <em>{previous_value}</em> '
                       '<strong>&rarr;</strong> {new_value} <br/>').format(
                       log_str=log_str,
                       field=field_name,
                       previous_value=previous_str,
                       new_value=new_str)

    elif obj.action_flag == 1:
        log_str = _('Record created')

    return mark_safe(log_str)


def format_jsonfield(data):
    out = ''
    if type(data) == list:
        for (key, value) in data[0].items():
            if value:
                value = value.encode('utf-8')
                if len(value) > 100:
                    value = value[0:100] + "..."
                if key != 'text':
                    out = out + key + ": " + value
                else:
                    out = out + value + " "
    elif type(data) == unicode:
        out = data.encode('utf-8')
    elif data != None:
        out = data

    return out
