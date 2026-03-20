from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

from django.http import HttpResponseForbidden
from django.dispatch import receiver
from django.core.cache import cache

from utils.context_processors import additional_user_info

from django.conf import settings

@receiver(user_logged_in)
def process_user_login(sender, request, user, **kwargs):
    # After first login add user info in cache
    additional_user_info(request)

@receiver(user_logged_out)
def process_user_logout(sender, request, user, **kwargs):
    # Delete user cache info
    user_info_key = f"user_info_{user.id}"
    cache.delete(user_info_key)
