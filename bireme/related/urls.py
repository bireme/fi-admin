from django.urls import path, re_path

from related.views import *

urlpatterns = [
    re_path(r'^ajax/get_passive_relations/(?P<ctype_id>\d+)/(?P<obj_id>.+)/?$', get_passive_relations, name='get_passive_relations'),
]
