from django.urls import path, re_path

from suggest import views as suggest_views

urlpatterns = [
    re_path(r'^suggest-resource/?$', suggest_views.suggest_resource, name='suggest_resource'),
    re_path(r'^suggested-resources/?$', suggest_views.list_suggestions, name='list_suggestions'),
    re_path(r'^suggested-resource/edit/(?P<resource_id>\d+)/?$', suggest_views.edit_suggested_resource, name='edit_suggested_resource'),

    re_path(r'^suggested-resource/create-resource-from-suggestion/(?P<suggestion_id>\d+)/?$', suggest_views.create_resource_from_suggestion, name='create_resource_from_suggestion'),
    re_path(r'^suggested-resource/create-event-from-suggestion/(?P<suggestion_id>\d+)/?$', suggest_views.create_event_from_suggestion, name='create_event_from_suggestion'),

    re_path(r'^suggest-tag/?$', suggest_views.suggest_tag, name='suggest_tag'),

    re_path(r'^suggest-event/?$', suggest_views.suggest_event, name='suggest_event'),
    re_path(r'^suggested-event/edit/(?P<suggest_id>\d+)/?$', suggest_views.edit_suggested_event, name='edit_suggested_event'),
]