from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from models import Help

def view_help(request, source_param, fieldname_param):
    """
    Receive source and field name and display help text
    """
    help = get_object_or_404(Help, source=source_param, field=fieldname_param)
    help_html = help.get_help()

    return HttpResponse(help_html)
