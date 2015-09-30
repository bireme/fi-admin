from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.utils.html import linebreaks

import json

register = template.Library()


def get_status_info(code):
    STATUS = (
        {'code': -1, 'label': _('Draft'), 'icons': 'icon-time status-draft'},
        {'code': 0, 'label': _('Pending'), 'icons': 'icon-flag status-pending'},
        {'code': 1, 'label': _('Admitted'), 'icons': 'icon-ok-sign status-ok'},
        {'code': 2, 'label': _('Refused'), 'icons': 'icon-ban-circle status-del'},
        {'code': 3, 'label': _('Deleted'), 'icons': 'icon-minus-sign status-del'},
    )
    status_info = [status for status in STATUS if status['code'] == code]

    return status_info[0]


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


@register.simple_tag(takes_context=True)
def display_field(context, field):
    object = context['object']

    field_value = getattr(object, field.name)
    # force convertion to list for values in JSON fields to proper format the value
    if fieldtype(field.field) == 'JSONFormField' and type(field_value) != list:
        field_value = json.loads(field_value)

    out = format_field(field_value)
    out = linebreaks(out)

    return out


@register.filter
def display_status_icon(status):
    status_info = get_status_info(status)

    out = '<span title="%s"><i class="%s"></i></span>' % (status_info['label'], status_info['icons'])
    return mark_safe(out)


@register.filter
def display_status(status):
    status_info = get_status_info(status)

    return status_info['label']


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
            if field_name == 'Status':
                previous_str = display_status(change['previous_value'])
                new_str = display_status(change['new_value'])
            else:
                previous_str = format_field(change['previous_value'], True)
                new_str = format_field(change['new_value'], True)

            log_str = ('{log_str}<strong>{field}:</strong> <em>{previous_value}</em> '
                       '<strong>&rarr;</strong> {new_value} <br/>').format(
                       log_str=log_str,
                       field=field_name,
                       previous_value=previous_str,
                       new_value=new_str)

    elif obj.action_flag == 1:
        log_str = _('Record created')

    return mark_safe(log_str)


@register.filter()
def format_field(data, truncate=False):
    out = ''
    if data:
        if type(data) == list:
            if type(data[0]) == dict:
                for (key, value) in data[0].items():
                    if value:
                        key = key.encode('utf-8')
                        value = value.encode('utf-8')
                        if truncate and len(value) > 100:
                            value = value[0:100] + "..."

                        if key != 'text':
                            out = out + "<span class='label'>" + key + "</span> " + value + " "
                        else:
                            out = out + value + " "
            else:
                out = ", ".join(data)
        elif type(data) == unicode:
            out = data.encode('utf-8')
        elif data is not None:
            out = data

    return out
