from django.urls import re_path

from utils import views as utils_views

urlpatterns = [
    re_path(r'^field_assist/(?P<field_name>\w+)/', utils_views.field_assist, name='field_assist'),
    re_path(r'^decs_suggestion/', utils_views.decs_suggestion, name='decs_suggestion'),
    re_path(r'^cookie-lang/?$', utils_views.cookie_lang, name='cookie_lang'),
]
