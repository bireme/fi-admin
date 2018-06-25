# coding: utf-8
# Django settings for fi-admin project.
import os, re

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

PROJECT_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT_PATH, 'database.db'),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'

LANGUAGES = (
    ('en', u'English'),
    ('pt-BR', u'Português'),
    ('es', u'Espanhol'),
)

LOCALE_PATHS =(
    os.path.join(PROJECT_ROOT_PATH, 'locale'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, 'uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT_PATH, 'static'),
    os.path.join(PROJECT_ROOT_PATH, 'uploads'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*3434mncic=m$-439jwsjll2327e+!_aq7xl)=cp9f@uedtjq'

DATE_INPUT_FORMATS = ('%d/%m/%Y')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',

    # thesaurus
    'django.core.context_processors.request',

    'django.contrib.messages.context_processors.messages',

    'utils.context_processors.additional_user_info',
    'utils.context_processors.django_settings',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'log.middleware.WhodidMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # Uncomment for Debug Toolbar
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'fi-admin.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'fi-admin.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    #'django_extensions',
    #'debug_toolbar',

    'haystack',
    'tastypie',
    'rosetta',
    'form_utils',
    'tinymce',

    'biremelogin',

    'api',
    'dashboard',
    'main',
    'events',
    'suggest',
    'error_reporting',
    'multimedia',
    'title',
    'biblioref',
    'leisref',
    'institution',
    'oer',
    'reports',
    'utils',
    'attachments',
    'help',
    'log',
    'text_block',
    'database',
    'classification',

    'thesaurus',

)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://localhost:8080/solr/fi'
    },
}

# Haystack signal for automatic update of Solr index when the model is saved/updated
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

SEARCH_SERVICE_URL = 'http://srv.bvsalud.org/'

DECS_LOOKUP_SERVICE = 'http://search.bvsalud.org/portal/decs-locator/?mode=dataentry'

RECAPTCHA_PRIVATE_KEY = ''

ITEMS_PER_PAGE = 20
LOGIN_URL = '/login/'

DEFAULT_COOPERATIVE_CENTER = 'BR1.1'

AUTHENTICATION_BACKENDS = (
    'biremelogin.authenticate.EmailModelBackend',
)

BIREMELOGIN_BASE_URL = "http://accounts.bireme.org"
SITE_URL = ""
BIREMELOGIN_SERVICE = ""
GOOGLE_ANALYTICS_ID = ""
VIEW_DOCUMENTS_BASE_URL = ""
DEDUP_SERVICE_URL = ""
VIEW_DEDUP_ARTICLE_DETAIL = ""
DEDUP_PUT_URL = ""

TINYMCE_JS_URL = "/static/js/tinymce/tinymce.min.js"

TINYMCE_DEFAULT_CONFIG = {
    'plugins': 'link table code',
    'theme': "modern",
    'menubar': False,
    'toolbar': 'undo redo | styleselect | bold italic | alignleft aligncenter alignright justify alignjustify | '
               'bullist numlist outdent indent | link image | table | code ',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}

# for settings_context_processor
TEMPLATE_VISIBLE_SETTINGS = (
    'GOOGLE_ANALYTICS_ID',
)

# don't registry changes at specific fields on audit log (ex. control fields)
EXCLUDE_AUDITLOG_FIELDS = ('content_type', 'object_id', 'reference_title',
                           'literature_type', 'code', 'short_url')

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# set permissions after file upload (444 read only file for security reasons)
FILE_UPLOAD_PERMISSIONS = 0444

# set max upload size
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_SIZE = "5242880"

# Debug toolbar settings
DEBUG_TOOLBAR = False
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1',)

try:
    from settings_local import *
except ImportError:
    pass
