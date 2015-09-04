from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

import json

register = template.Library()

@register.filter
def fieldtype(obj):
    return obj.__class__.__name__

@register.filter
def invalues(value, list):
    find = [item for item in list if item[1] == value]
    if find:
        find = True

    return find

@register.filter
def profilefield(user, field):
    return user.profile.get_attribute(field)


@register.filter()
def log_json_changes(obj):
    log_str = ''
    if obj.change_message:
        data = json.loads(obj.change_message)
        model = obj.content_type.model_class()

        for change in data:
            # ignore changes from where previous and new are null or blank. Ex. null to blank
            if not change['previous_value'] and not change['new_value']:
                continue

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
    if data:
        if type(data) == list:
            if type(data[0]) == dict:
                for (key, value) in data[0].items():
                    if value:
                        value = value.encode('utf-8')
                        if len(value) > 100:
                            value = value[0:100] + "..."
                        if key != 'text':
                            out = out + key + ": " + value
                        else:
                            out = out + value + " "
            else:
                out = ", ".join(data)
        elif type(data) == unicode:
            out = data.encode('utf-8')
        elif data != None:
            out = data

    return out
