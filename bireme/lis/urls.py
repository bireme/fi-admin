from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.conf import settings

from main.api import ResourceAPI

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

resource_api = ResourceAPI()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lis.views.home', name='home'),
    # url(r'^lis/', include('lis.foo.urls')),

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

    # Topics 
    (r'^topics/?$', 'main.views.list_topics'),
    (r'^topic/new/?$', 'main.views.create_edit_topic'),
    (r'^topic/edit/(?P<topic_id>\d+)/?$', 'main.views.create_edit_topic'),

    # Types
    (r'^types/?$', 'main.views.list_types'),
    (r'^type/new/?$', 'main.views.create_edit_type'),
    (r'^type/edit/(?P<type_id>\d+)/?$', 'main.views.create_edit_type'),


    url(r'^login/$', auth_views.login, {'template_name': 'authentication/login.html'}, name='auth_login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'authentication/logout.html', 'next_page': '/'}, name='auth_logout'),

    (r'^api/', include(resource_api.urls)),

    (r'^$', 'main.views.dashboard'),
)


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
