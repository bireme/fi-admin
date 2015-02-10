from django import template

register = template.Library()

@register.filter
def fieldtype(obj):
    return obj.__class__.__name__