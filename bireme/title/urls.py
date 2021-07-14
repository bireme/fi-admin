from django.urls import path, re_path

from title.views import *

urlpatterns = [
    path('', TitleListView.as_view(), name='list_title'),
    re_path(r'^new/?$', TitleCreateView.as_view(), name='create_title'),
    re_path(r'^edit/(?P<pk>\d+)/?$', TitleUpdateView.as_view(), name='edit_title'),
    re_path(r'^delete/(?P<pk>\d+)/?$', TitleDeleteView.as_view(), name='delete_title'),
    re_path(r'^preview/(?P<pk>\d+)/?$', TitlePreview.as_view(), name='preview_title'),

    re_path(r'^ajax/search/$', search_title, name='search_title'),
    re_path(r'^ajax/get_indexcodes/$', get_indexcodes, name='get_indexcodes'),
]
