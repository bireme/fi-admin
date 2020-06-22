from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Collection, Relationship

import json

def classify(request, ctype_id, obj_id):
    set_list_param = request.POST.getlist('set')
    unset_list_param = request.POST.getlist('unset')
    updated = (set_list_param or unset_list_param)
    relation_list = []

    if set_list_param or unset_list_param:
        # remove duplicated ID's from set/unset lists
        set_list = list(set(set_list_param))
        unset_list = list(set(unset_list_param))

        for col_id in set_list:
            new_relation, created = Relationship.objects.get_or_create(object_id=obj_id, content_type_id=ctype_id, collection_id=col_id)

        if unset_list:
            Relationship.objects.filter(object_id=obj_id, content_type_id=ctype_id, collection_id__in=unset_list).delete()

    # community = collection of first level (without parent)
    community_list = Collection.objects.filter(parent__isnull=True)

    relationships = Relationship.objects.filter(content_type_id=ctype_id, object_id=obj_id)
    relation_list = [rel.collection  for rel in relationships]
    relation_list_ids = [int(rel.collection_id)  for rel in relationships]

    return render_to_response('classification/classify.html',
                              {'relation_list': relation_list, 'community_list': community_list, 'c_type': ctype_id,
                               'object_id': obj_id, 'relation_list_ids': relation_list_ids, 'updated': updated},
                              context_instance=RequestContext(request))




def get_children_list(request, parent_id):
    children_list = []
    children_type = ''

    children_list = [dict({'value': col.id, 'name': unicode(col)}) for col in Collection.objects.filter(parent=parent_id, community_flag=True)]
    if children_list:
        children_type = 'community'
    else:
        children_list = [dict({'value': col.id, 'name': unicode(col)}) for col in Collection.objects.filter(parent=parent_id)]
        if children_list:
            children_type = 'collection'


    out_list = dict({'type': children_type, 'list': children_list})
    data = json.dumps(out_list)

    return HttpResponse(data, content_type='application/json')
