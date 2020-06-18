from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^classify/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', classify, name="classify"),
    url(r'^get-children-list/(?P<parent_id>\d+)/?$', get_children_list, name='get_children_list'),
)
