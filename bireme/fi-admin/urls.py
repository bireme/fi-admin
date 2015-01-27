from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.conf import settings

from api.resources_api import LinkResource
from api.events_api import EventResource
from api.multimedia_api import MediaResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

link_resource = LinkResource()
event_resource = EventResource()
media_resource = MediaResource()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'fi-admin.views.home', name='home'),
    # url(r'^fi-admin/', include('fi-admin.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    (r'^cookie-lang/?$', 'utils.views.cookie_lang'),

    # Resources
    (r'^resources/?$', 'main.views.list_resources'),
    (r'^resource/new/?$', 'main.views.create_edit_resource'),
    (r'^resource/edit/(?P<resource_id>\d+)/?$', 'main.views.create_edit_resource'),

    # Events
    (r'^events/?$', 'events.views.list_events'),
    (r'^event/new/?$', 'events.views.create_edit_event'),
    (r'^event/edit/(?P<event_id>\d+)/?$', 'events.views.create_edit_event'),


    # Thematic areas
    (r'^thematics/?$', 'main.views.list_thematics'),
    (r'^thematic/new/?$', 'main.views.create_edit_thematic'),
    (r'^thematic/edit/(?P<thematic_id>\d+)/?$', 'main.views.create_edit_thematic'),

    # Source types
    (r'^types/?$', 'main.views.list_types'),
    (r'^type/new/?$', 'main.views.create_edit_type'),
    (r'^type/edit/(?P<type_id>\d+)/?$', 'main.views.create_edit_type'),

    # Event types
    (r'^event-types/?$', 'events.views.list_types'),
    (r'^event-type/new/?$', 'events.views.create_edit_type'),
    (r'^event-type/edit/(?P<type_id>\d+)/?$', 'events.views.create_edit_type'),


    # Source languages
    (r'^languages/?$', 'main.views.list_languages'),
    (r'^language/new/?$', 'main.views.create_edit_language'),
    (r'^language/edit/(?P<language_id>\d+)/?$', 'main.views.create_edit_language'),


    # Suggest
    (r'^suggest-resource/?$', 'suggest.views.suggest_resource'),
    (r'^suggested-resources/?$', 'suggest.views.list_suggestions'),
    (r'^suggested-resource/edit/(?P<resource_id>\d+)/?$', 'suggest.views.edit_suggested_resource'),

    (r'^suggested-resource/create-resource-from-suggestion/(?P<suggestion_id>\d+)/?$', 'suggest.views.create_resource_from_suggestion'),
    (r'^suggested-resource/create-event-from-suggestion/(?P<suggestion_id>\d+)/?$', 'suggest.views.create_event_from_suggestion'),

    (r'^suggest-tag/?$', 'suggest.views.suggest_tag'),

    (r'^suggest-event/?$', 'suggest.views.suggest_event'),
    (r'^suggested-event/edit/(?P<suggest_id>\d+)/?$', 'suggest.views.edit_suggested_event'),

    # Error reporting
    (r'^error-reporting/?$', 'error_reporting.views.list_error_report'),
    (r'^error-reporting/new/?$', 'error_reporting.views.create_error_report'),
    (r'^error-reporting/edit/(?P<report_id>\d+)/?$', 'error_reporting.views.edit_error_report'),
    # External error report
    (r'^report-error/?$', 'error_reporting.views.external_error_report'),

    # Multimedia
    (r'^multimedia/', include('multimedia.urls')),

    # Bibliographic References
    (r'^bibliographic/', include('biblioref.urls')),

    # Login/Logout
    url(r'^login/$', auth_views.login, {'template_name': 'authentication/login.html', 'extra_context':{'BIREMELOGIN_BASE_URL': settings.BIREMELOGIN_BASE_URL}}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'authentication/logout.html', 'next_page': '/'}, name='auth_logout'),

    # API's
    (r'^api/', include(link_resource.urls)),
    (r'^api/', include(event_resource.urls)),
    (r'^api/', include(media_resource.urls)),
    (r'^api/lis-old/search/', 'api.lis_old_api.search'),

    #internationalization
    url(r'^i18n/', include('django.conf.urls.i18n')),
    (r'^cookie-lang/?$', 'utils.views.cookie_lang'),

    (r'^$', 'main.views.dashboard'),
)


# messages translation
if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
