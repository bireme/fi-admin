from django import template
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from django.utils.html import linebreaks
from django.core.exceptions import FieldDoesNotExist

from utils.models import AuxCode

import json

register = template.Library()


def get_status_info(code):
    STATUS = (
        {'code': -3, 'label': _('Migration'), 'icons': 'icon-upload status-migration', 'label_color': 'important'},
        {'code': -2, 'label': _('Submission'), 'icons': 'icon-upload status-submission', 'label_color': 'inverse'},
        {'code': -1, 'label': _('Draft'), 'icons': 'icon-time status-draft', 'label_color': ''},
        {'code': 0, 'label': 'LILACS-Express', 'icons': 'icon-flag status-pending', 'label_color': 'info'},
        {'code': 1, 'label': _('Published'), 'icons': 'icon-ok-sign status-ok', 'label_color': 'success'},
        {'code': 2, 'label': _('Refused'), 'icons': 'icon-ban-circle status-del', 'label_color': 'warning'},
        {'code': 3, 'label': _('Deleted'), 'icons': 'icon-minus-sign status-del', 'label_color': 'important'},
        # Thesaurus
        {'code': 5, 'label': _('Historical'), 'icons': 'icon-upload status-migration', 'label_color': 'important'},
        {'code': 10, 'label': _('Awaiting translation'), 'icons': 'icon-upload status-migration', 'label_color': 'warning'},

    )
    status_info = [status for status in STATUS if status['code'] == int(code)]

    return status_info[0]

def get_change_info(label):
    STATUS = (
        {'label': 'new', 'label_text' : _('new'), 'label_color': 'success'},
        {'label': 'deleted', 'label_text' : _('deleted'), 'label_color': 'important'},
    )
    change_info = [status for status in STATUS if status['label'] == label]

    return change_info[0]

@register.filter
def fieldtype(obj):
    return obj.__class__.__name__

@register.filter
def widgetfieldtype(obj):
    return obj.widget.__class__.__name__

@register.filter
def invalues(value, list):
    find = [item for item in list if item[0] == value]
    if find:
        find = True

    return find

@register.filter
def infieldset(name, fieldsets):
    find = False
    for fieldset in fieldsets:
        if fieldset.name == name:
            find = True

    return find

@register.filter
def inintvalues(value, list):
    # convert parameters to int
    pkvalue = int(value)
    pkvalue_list = [int(v) for v in list]

    find = pkvalue in pkvalue_list
    return find


@register.filter
def profilefield(user, field):
    return user.profile.get_attribute(field)

@register.simple_tag
def get_field_display(object, field, sep=' '):
    ft = fieldtype(field.field)
    widget = widgetfieldtype(field.field)

    if widget == 'Select':
        # check if is foreign key
        if ft == 'ModelChoiceField':
            out = getattr(object, field.name)
        else:
            out = getattr(object, 'get_%s_display' % field.name)()
    elif widget == 'SelectMultiple':
        list = []
        for index in field.form[field.name][0].value:
            list += [dict(field.field.choices)[int(index)]]
        # query = getattr(object, field.name).all()
        # out = sep.join(str(i) for i in query)
        out = sep.join(list)

    return out

@register.simple_tag(takes_context=True)
def display_field(context, field):
    object = context['object']

    field_value = getattr(object, field.name)
    # force convertion to list for values in JSON fields to proper format the value
    if fieldtype(field.field) == 'JSONField' and type(field_value) != list:
        field_value = json.loads(field_value)

    # check if field has multiples values (ex. ManyToManyField)
    if hasattr(field_value, 'all'):
        # create list of values for presentation
        field_value = [value for value in field_value.all()]

    out = format_field(field_value)
    out = linebreaks(out)

    return out

@register.filter
def display_json_value(value):
    if not isinstance(value, str):
        value = str(value)
        value = value.replace("'", '\"')
        field_value = value
    else:
        if value.startswith('[{'):
            field_value = json.loads(value)
        else:
            field_value = value

    out = format_field(field_value)
    return out

@register.filter
def display_status_icon(status):
    status_info = get_status_info(status)
    out = '<span title="%s"><i class="%s"></i></span>' % (status_info['label'], status_info['icons'])

    return mark_safe(out)


@register.filter
def display_status_label(status):
    status_info = get_status_info(status)
    out = '<span class="label label-%s">%s</span>' % (status_info['label_color'], status_info['label'])

    return mark_safe(out)


@register.filter
def display_status(status):
    status_info = get_status_info(status)

    return status_info['label']


@register.filter()
def log_json_changes(obj):
    log_str = ''
    data = None

    if obj.change_message and obj.change_message != '':
        try:
            data = json.loads(obj.change_message)
        except:
            log_str = obj.change_message

        if type(data) is list:
            model = obj.content_type.model_class()
            for change in data:
                # ignore changes from where previous and new are null or blank. Ex. null to blank
                if not change['previous_value'] and not change['new_value']:
                    continue

                try:
                    field_name = model._meta.get_field(change['field_name']).verbose_name
                except:
                    field_name = change['field_name']

                if field_name == 'Status':
                    previous_str = display_status(change['previous_value'])
                    new_str = display_status(change['new_value'])
                else:
                    previous_str = format_field(change['previous_value'], True)
                    new_str = format_field(change['new_value'], True)

                label_str = ''
                if 'label' in change:
                    change_label = get_change_info(change['label'])
                    label_str = '<span class="label label-%s">%s</span> ' % (change_label['label_color'], change_label['label_text'])

                log_str = ('{log_str}{label}<strong>{field}:</strong> <em>{previous_value}</em> '
                           '<strong>&rarr;</strong> {new_value} <br/>').format(
                           label=label_str,
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
            for data_occ in data:
                if type(data_occ) == dict:
                    for (key, value) in data_occ.items():
                        if value:
                            key = key
                            if not isinstance(value, str):
                                value = str(value)
                            value = value
                            if truncate and len(value) > 100:
                                value = value[0:100] + "..."

                            if key != 'text':
                                out = out + "<span class='label'>" + key + "</span> " + value + " "
                            else:
                                out = out + value + " "

                    out = out + "<br/>"
                else:
                    # encode list items to utf-8
                    data_utf8 = [value if isinstance(value, str) else str(value) for value in data]
                    out = ", ".join(data_utf8)

        elif type(data) == str:
            out = data
        elif data is not None:
            out = data

    return out


@register.filter
def substring_after(text, delim):
    return text.partition(delim)[2]


@register.filter
def substring_before(text, delim):
    return text.partition(delim)[0]


@register.filter
def auxfield(field):
    aux_values = AuxCode.objects.filter(field=field.name)

    return aux_values

@register.filter
def field_has_error(form, field):

    return form.has_error(field)

def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


@register.filter
def display_field_label(field_name, class_name):
    model = get_class(class_name)
    try:
        field = model._meta.get_field(field_name)
        field_label = field.verbose_name
    except FieldDoesNotExist:
        field_label = field_name

    return field_label.capitalize()
