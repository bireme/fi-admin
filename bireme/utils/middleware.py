from django.shortcuts import reverse, redirect
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get('PATH_INFO', "")

        if settings.MAINTENANCE_MODE:
            # redirect all except django-admin to maintenance page
            if  not '/admin/' in path and path != reverse("maintenance"):
                response = redirect(reverse("maintenance"))
                return response

        response = self.get_response(request)

        return response

class BruteForceProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if the request is for the login page and the method is POST
        if request.path == settings.LOGIN_URL and request.method == "POST":

            # Get the IP address of the client
            ip_address = request.META.get("REMOTE_ADDR")

            # Increment the failed login attempt count for this IP address
            cache_key = f"login_attempts:{ip_address}"

            login_attempts = cache.get(cache_key, 0)

            # Save attemp in cache
            cache.set(cache_key, login_attempts + 1, timeout=settings.BRUTE_FORCE_TIMEOUT)

            # If the login attempts exceed the threshold, block further attempts
            if login_attempts >= settings.BRUTE_FORCE_THRESHOLD:
                time_to_wait = settings.BRUTE_FORCE_TIMEOUT // 60
                return HttpResponseForbidden(
                    f"Too many login attempts. Please try again later after {time_to_wait} minutes."
                )

        return response
