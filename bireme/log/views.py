from django.http import HttpResponse

from django.shortcuts import render_to_response
from django.contrib.admin.models import LogEntry

def view_log(request, ctype_id, obj_id):
    """
    Receive source and field name and display help text
    """
    logs = LogEntry.objects.filter(content_type_id=ctype_id, object_id=obj_id)

    return render_to_response('log/list.html', {'logs': logs})
