#! coding: utf-8
import requests

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import ThematicArea


@csrf_exempt
def get_thematic_id(request, thematic_acronym):

    thematic_id = 'NOT FOUND'
    if thematic_acronym:
        try:
            thematic_id = ThematicArea.objects.get(acronym=thematic_acronym).id
        except:
            pass

    return HttpResponse(thematic_id)
