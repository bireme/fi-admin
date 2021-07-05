from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf import settings
from short_url import decode_url
from datetime import datetime, timezone

from attachments.models import Attachment

def view_document(request, short_id):
    """
    Receive short_id of the document, decode and redirect to complete url of the document on server
    """

    doc_id = decode_url(short_id)
    doc = get_object_or_404(Attachment, pk=doc_id)

    # temporary check for validation of alternative environment python3
    date_start_fiadmin2 = datetime(2021, 7, 2, tzinfo=timezone.utc)
    view_documents_url = settings.VIEW_DOCUMENTS_BASE_URL if doc.created_time > date_start_fiadmin2 else 'https://docs.bvsalud.org'

    #document_url = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, doc.attachment_file)
    document_url = '%s/%s' % (view_documents_url, doc.attachment_file)

    return redirect(document_url)
