from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^view/(?P<ctype_id>\w{0,30})/(?P<obj_id>\d+)/?$', view_log),
)
