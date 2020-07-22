from django.urls import path, re_path

from main import views as main_views

app_name = 'main'

urlpatterns = [
    # Resources
    re_path(r'^resources/?$', main_views.list_resources, name='list_resources'),
    re_path(r'^resource/new/?$', main_views.create_edit_resource, name='create_resource'),
    re_path(r'^resource/edit/(?P<resource_id>\d+)/?$', main_views.create_edit_resource, name='edit_resource'),

    # Thematic areas
    re_path(r'^thematics/?$', main_views.list_thematics, name='list_thematics'),
    re_path(r'^thematic/new/?$', main_views.create_edit_thematic, name='create_thematic'),
    re_path(r'^thematic/edit/(?P<thematic_id>\d+)/?$', main_views.create_edit_thematic, name='edit_thematic'),

    # Source types
    re_path(r'^types/?$', main_views.list_types, name='list_types'),
    re_path(r'^type/new/?$', main_views.create_edit_type, name='create_type'),
    re_path(r'^type/edit/(?P<type_id>\d+)/?$', main_views.create_edit_type, name='edit_type'),

    # Source languages
    re_path(r'^languages/?$', main_views.list_languages, name='list_languages'),
    re_path(r'^language/new/?$', main_views.create_edit_language, name='create_language'),
    re_path(r'^language/edit/(?P<language_id>\d+)/?$', main_views.create_edit_language, name='edit_language'),
]