from django.urls import re_path

from help import views as help_views

urlpatterns = [
    re_path(r'^view/(?P<source_param>\w{0,35})/(?P<fieldname_param>\w{0,55})/?$', help_views.view_help, name='view_help'),
]
