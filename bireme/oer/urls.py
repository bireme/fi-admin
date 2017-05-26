from django.conf.urls import url

from views import *

urlpatterns = [
    # OER
    url(r'^/?$', OERListView.as_view(), name='list_oer'),
    url(r'^new/?$', OERCreateView.as_view(), name='create_oer'),
    url(r'^edit/(?P<pk>\d+)/?$', OERUpdateView.as_view(), name='edit_oer'),
    url(r'^delete/(?P<pk>\d+)/?$', OERDeleteView.as_view(), name='delete_oer'),
    url(r'^oer-related/?$', OERRelatedListView.as_view(), name='oer_related'),
    
    url(r'^field_assist/(?P<field_name>\w+)/', field_assist, name='field_assist'),
]
