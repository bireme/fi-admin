from django.urls import path, re_path
from django.contrib.auth import views as auth_views

from django.conf import settings

urlpatterns = [
    # Login/Logout
    re_path(r'^login/$', auth_views.LoginView.as_view(template_name='authentication/login.html',
                                                    extra_context={'BIREMELOGIN_BASE_URL': settings.BIREMELOGIN_BASE_URL}),
                                                    name='auth_login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(template_name='authentication/logout.html', next_page='/'), name='auth_logout'),
]