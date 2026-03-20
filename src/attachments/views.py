from django.shortcuts import get_object_or_404
from django.http import Http404
from django.shortcuts import redirect
from django.conf import settings
from short_url import decode_url
from datetime import datetime, timezone

from attachments.models import Attachment

def view_document(request, short_id):
    """
    Receive short_id of the document, decode and redirect to complete url of the document on server
    """

    try:
        doc_id = decode_url(short_id)
    except ValueError:
        raise Http404("Invalid document id")

    doc = get_object_or_404(Attachment, pk=doc_id)

    document_url = '%s/%s' % (settings.VIEW_DOCUMENTS_BASE_URL, doc.attachment_file)

    return redirect(document_url)
