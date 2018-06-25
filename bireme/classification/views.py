from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Term, Relationship

def show_classification(request, ctype_id, obj_id):
    term_list = Term.objects.filter(type=1, parent__isnull=True)
    relationships = Relationship.objects.filter(content_type_id=ctype_id, object_id=obj_id)
    relation_list = [rel.term_id  for rel in relationships]

    return render_to_response('classification/show.html',
                              {'relation_list': relation_list, 'term_list': term_list, 'c_type': ctype_id, 'object_id': obj_id},
                              context_instance=RequestContext(request))


def update_classification(request):
    ctype_id = request.POST.get('c_type')
    object_id = request.POST.get('object_id')
    set_list_param = request.POST.getlist('set')
    unset_list_param = request.POST.getlist('unset')

    # remove duplicated ID's from set/unset lists
    set_list = list(set(set_list_param))
    unset_list = list(set(unset_list_param))

    for term_id in set_list:
        new_relation, created = Relationship.objects.get_or_create(object_id=object_id, content_type_id=ctype_id, term_id=term_id)

    if unset_list:
        Relationship.objects.filter(object_id=object_id, content_type_id=ctype_id, term_id__in=unset_list).delete()

    return HttpResponse(status=200)
