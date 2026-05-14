from biblioref.models import *
from biblioref.search_indexes import *

import json

def fix_json(field_value):
    if field_value.startswith('"'):
        # remove first and last " of string
        field_value = field_value[1:-1]

    # unescape string
    field_value = field_value.replace('\\"','"').replace('\\r\\n', '\r\n')

    return field_value

# records = Reference.objects.filter(created_by_id=224, indexed_database=21)
records = Reference.objects.filter(id=1)
check_field_list = ['abstract']

for r in records:
    print r
    need_update = False
    for field in check_field_list:
        field_value = getattr(r, field)
        # check if field is a list (json) otherwise convert
        if type(field_value) != list:
            print "Need update"
            need_update = True
            fixed_value = fix_json(field_value)
            setattr(r, field, fixed_value)

    if need_update:
        r.save()
