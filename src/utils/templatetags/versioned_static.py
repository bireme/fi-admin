import hashlib
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


def file_hash(path):
    """Short md5 of a static file's content, or None if the file is not found."""
    absolute_path = finders.find(path)
    if not absolute_path:
        return None
    with open(absolute_path, 'rb') as f:
        return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()[:8]


cached_file_hash = lru_cache(maxsize=None)(file_hash)


@register.simple_tag
def versioned_static(path):
    """
    Static URL with a content-hash query string (?v=...), so browsers fetch the
    file again when it changes. Hash is cached per process; recomputed on every
    call when DEBUG is on so edits show up without restarting runserver.
    """
    digest = file_hash(path) if settings.DEBUG else cached_file_hash(path)
    url = static(path)
    return f'{url}?v={digest}' if digest else url
