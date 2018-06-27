from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Collection, Relationship

def classify(request, ctype_id, obj_id):
    collection_param = request.POST.get('collection')
    set_list_param = request.POST.getlist('set')
    unset_list_param = request.POST.getlist('unset')
    relation_list = []

    if set_list_param or unset_list_param:
        # remove duplicated ID's from set/unset lists
        set_list = list(set(set_list_param))
        unset_list = list(set(unset_list_param))

        for col_id in set_list:
            new_relation, created = Relationship.objects.get_or_create(object_id=obj_id, content_type_id=ctype_id, collection_id=col_id)

        if unset_list:
            Relationship.objects.filter(object_id=obj_id, content_type_id=ctype_id, collection_id__in=unset_list).delete()


    collection_list = Collection.objects.filter(parent__isnull=True)
    if collection_param:
        relationships = Relationship.objects.filter(content_type_id=ctype_id, object_id=obj_id)
        relation_list = [rel.collection_id  for rel in relationships]


    return render_to_response('classification/classify.html',
                              {'relation_list': relation_list, 'collection_list': collection_list, 'c_type': ctype_id,
                               'object_id': obj_id, 'collection_param': collection_param},
                              context_instance=RequestContext(request))
