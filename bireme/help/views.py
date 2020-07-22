from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings

from help.models import Help

def view_help(request, source_param, fieldname_param):
    """
    Receive source and field name and display help text
    """
    page = request.GET.get('page', None)
    output = {}

    help = get_object_or_404(Help, source=source_param, field=fieldname_param)
    help_html = help.get_help()

    if page:
        output['help'] = help_html
        return render(request, 'help/page.html', output)
    else:
        return HttpResponse(help_html)
