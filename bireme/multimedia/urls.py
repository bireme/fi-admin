from django.urls import re_path

from multimedia.views import *

urlpatterns = [

    # Multimedia
    re_path(r'^/?$', MediaListView.as_view(), name='list_media'),
    re_path(r'^new/?$', MediaCreateView.as_view(), name='create_media'),
    re_path(r'^edit/(?P<pk>\d+)/?$', MediaUpdateView.as_view(), name='edit_media'),
    re_path(r'^delete/(?P<pk>\d+)/?$', MediaDeleteView.as_view(), name='delete_media'),

    # Multimedia collections
    re_path(r'^collections/?$', MediaCollectionListView.as_view(), name='list_mediacollections'),
    re_path(r'^collection/new/?$', MediaCollectionCreateView.as_view(), name='create_mediacollection'),
    re_path(r'^collection/edit/(?P<pk>\d+)/?$', MediaCollectionEditView.as_view(), name='edit_mediacollection'),
    re_path(r'^collection/delete/(?P<pk>\d+)/?$', MediaCollectionDeleteView.as_view(), name='delete_mediacollection'),


    # Media types
    re_path(r'^media-types/?$', MediaTypeListView.as_view(), name='list_mediatypes'),
    re_path(r'^media-type/new/?$', MediaTypeCreateView.as_view(), name='create_mediatype'),
    re_path(r'^media-type/edit/(?P<pk>\d+)/?$', MediaTypeUpdateView.as_view(), name='edit_mediatype'),
    re_path(r'^media-type/delete/(?P<pk>\d+)/?$', MediaTypeDeleteView.as_view(), name='delete_mediatype'),
]
