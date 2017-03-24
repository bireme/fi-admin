from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^view/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', view_log, name="view_log"),
    url(r'^review/(?P<type>\w{0,15})/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', review_log, name="review_log"),
    url(r'^update-review/?$', update_review, name="update_review"),
)
