from django.urls import re_path

from oer.views import *

urlpatterns = [
    # OER
    re_path(r'^/?$', OERListView.as_view(), name='list_oer'),
    re_path(r'^new/?$', OERCreateView.as_view(), name='create_oer'),
    re_path(r'^edit/(?P<pk>\d+)/?$', OERUpdateView.as_view(), name='edit_oer'),
    re_path(r'^delete/(?P<pk>\d+)/?$', OERDeleteView.as_view(), name='delete_oer'),
    re_path(r'^oer-related/?$', OERRelatedListView.as_view(), name='oer_related'),

    re_path(r'^field_assist/(?P<field_name>\w+)/', field_assist, name='field_assist'),
]
