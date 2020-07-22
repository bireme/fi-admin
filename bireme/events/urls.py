from django.urls import path, re_path

from events import views as events_views

app_name = 'events'

urlpatterns = [
    re_path(r'^events/?$', events_views.list_events, name='list_events'),
    re_path(r'^event/new/?$', events_views.create_edit_event, name='create_event'),
    re_path(r'^event/edit/(?P<event_id>\d+)/?$', events_views.create_edit_event, name='edit_event'),

    # Event types
    re_path(r'^event-types/?$', events_views.list_types, name='list_types'),
    re_path(r'^event-type/new/?$', events_views.create_edit_type, name='create_type'),
    re_path(r'^event-type/edit/(?P<type_id>\d+)/?$', events_views.create_edit_type, name='edit_type'),
]