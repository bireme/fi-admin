from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

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

    (r'^resources/?$', 'main.views.list_resources'),
    (r'^resource/new/?$', 'main.views.create_edit_resource'),
    (r'^resource/edit/(?P<resource_id>\d+)/?$', 'main.views.create_edit_resource'),

    (r'^$', 'main.views.dashboard'),

)


if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
