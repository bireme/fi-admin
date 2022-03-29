#! coding: utf-8
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from biblioref.models import Reference
from related.models import *


def get_passive_relations(request, ctype_id, obj_id):
    passive_relations = LinkedResource.objects.filter(content_type_id=ctype_id, internal_id=obj_id)
    passive_relations_list = [{"title": Reference.objects.get(pk=rel.object_id).reference_title, "relation_type": rel.type.field_passive.name} for rel in passive_relations]

    passive_relations_response = json.dumps(passive_relations_list, cls=DjangoJSONEncoder)


    return HttpResponse(passive_relations_response, content_type="application/json")