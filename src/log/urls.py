from django.urls import re_path

from log import views as log_views

urlpatterns = [
    re_path(r'^view/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', log_views.view_log, name="view_log"),
    re_path(r'^review/(?P<type>\w{0,15})/(?P<ctype_id>\d+)/(?P<obj_id>\d+)/?$', log_views.review_log, name="review_log"),
    re_path(r'^update-review/?$', log_views.update_review, name="update_review"),
]
