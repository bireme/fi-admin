from django.conf.urls import url

from views import * 

urlpatterns = [

    # Multimedia
    url(r'^/?$', MediaListView.as_view(), name='list_media'),
    url(r'^new/?$', MediaCreateView.as_view(), name='create_media'),
    url(r'^edit/(?P<pk>\d+)/?$', MediaUpdateView.as_view(), name='edit_media'),
    url(r'^delete/(?P<pk>\d+)/?$', MediaDeleteView.as_view(), name='delete_media'),
    
    # Media types
    url(r'^media-types/?$', MediaTypeListView.as_view(), name='list_mediatypes'),
    url(r'^media-type/new/?$', MediaTypeCreateView.as_view(), name='create_mediatype'),
    url(r'^media-type/edit/(?P<pk>\d+)/?$', MediaTypeUpdateView.as_view(), name='edit_mediatype'),
    url(r'^media-type/delete/(?P<pk>\d+)/?$', MediaTypeDeleteView.as_view(), name='delete_mediatype'),    
]

