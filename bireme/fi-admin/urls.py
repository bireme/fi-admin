from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.conf import settings

# enable django admin:
from django.contrib import admin
admin.autodiscover()


if settings.EXPOSE_API_ONLY:
    urlpatterns = [
        re_path(r'^api/', include('api.urls')),
    ]
else:
    urlpatterns = [
        path('', include('dashboard.urls')),
        path('', include('main.urls')),
        path('', include('events.urls')),
        path('', include('suggest.urls')),
        path('', include('biremelogin.urls')),
        path('', include('error_reporting.urls')),

        # Django Admin
        re_path(r'^admin/', admin.site.urls),

        # Bibliographic Records
        re_path(r'^bibliographic/', include('biblioref.urls')),

        # Title
        re_path(r'^title/', include('title.urls')),

        # Issues
        # (r'^issues/', include('issues.urls')),

        # Reports
        re_path(r'^reports/', include('reports.urls')),

        # Institution
        re_path(r'^institution/', include('institution.urls')),

        # Multimedia
        re_path(r'^multimedia/', include('multimedia.urls')),

        # Legislation
        re_path(r'^legislation/', include('leisref.urls')),

        # Open Educational Resource
        re_path(r'^oer/', include('oer.urls')),

        # Thesaurus
        re_path(r'^thesaurus/', include('thesaurus.urls')),

        # Reports
        re_path(r'^reports/', include('reports.urls')),

        # Attachments
        re_path(r'^document/', include('attachments.urls')),

        # Classification
        re_path(r'^classification/', include('classification.urls')),

        # APIs
        re_path(r'^api/', include('api.urls')),

        # Help
        re_path(r'^help/', include('help.urls')),

        # Logs
        re_path(r'^log/', include('log.urls')),

        # Internationalization
        re_path(r'^i18n/', include('django.conf.urls.i18n')),

        # Utils
        re_path(r'^utils/', include('utils.urls')),

        # Tinymce wysiwyg editor
        re_path(r'^tinymce/', include('tinymce.urls')),

        # Maintenance
        re_path(r'^maintenance/', TemplateView.as_view(template_name="maintenance.html")),

    ]

    # messages translation
    if 'rosetta' in settings.INSTALLED_APPS:
        urlpatterns += [
            re_path(r'^rosetta/', include('rosetta.urls')),
        ]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
