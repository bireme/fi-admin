from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^view/(?P<source_param>\w{0,35})/(?P<fieldname_param>\w{0,55})/?$', view_help),
)
