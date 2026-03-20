from django.urls import re_path

from classification import views as classification_views

urlpatterns = [
    re_path(r'^classify/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', classification_views.classify, name="classify"),
    re_path(r'^get-children-list/(?P<parent_id>\d+)/?$', classification_views.get_children_list, name='get_children_list'),
]
