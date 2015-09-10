from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',
    url(r'^view/(?P<short_id>\w{0,30})?$', view_document),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
