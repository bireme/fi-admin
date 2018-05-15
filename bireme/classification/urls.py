from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^show/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', show_classification, name="show_classification"),
    url(r'^update/?$', update_classification, name="update_classification"),
)
