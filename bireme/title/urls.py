from django.urls import re_path

from title.views import *

urlpatterns = [
    re_path(r'^/?$', TitleListView.as_view(), name='list_title'),
    re_path(r'^new/?$', TitleCreateView.as_view(), name='create_title'),
    re_path(r'^edit/(?P<pk>\d+)/?$', TitleUpdateView.as_view(), name='edit_title'),
    re_path(r'^delete/(?P<pk>\d+)/?$', TitleDeleteView.as_view(), name='delete_title'),
    re_path(r'^preview/(?P<pk>\d+)/?$', TitlePreview.as_view(), name='preview_title'),
]
