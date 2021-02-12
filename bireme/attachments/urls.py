from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

from attachments import views as attachments_views

app_name = 'attachments'

urlpatterns = [
    re_path(r'^view/(?P<short_id>\w{0,30})?$', attachments_views.view_document, name='view_document'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
