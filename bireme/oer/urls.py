from django.conf.urls import url

from views import *

urlpatterns = [
    # OER
    url(r'^/?$', OERListView.as_view(), name='list_oer'),
    url(r'^new/?$', OERCreateView.as_view(), name='create_oer'),
    url(r'^edit/(?P<pk>\d+)/?$', OERUpdateView.as_view(), name='edit_oer'),
    url(r'^delete/(?P<pk>\d+)/?$', OERDeleteView.as_view(), name='delete_oer'),

    # Aux OER Type
    url(r'^aux-oer-type/?$', OERTypeListView.as_view(), name='list_oer_type'),
    url(r'^aux-oer-type/new/?$', OERTypeCreateView.as_view(), name='create_oer_type'),
    url(r'^aux-oer-type/edit/(?P<pk>\d+)/?$', OERTypeUpdateView.as_view(), name='edit_oer_type'),
    url(r'^aux-oer-type/delete/(?P<pk>\d+)/?$', OERTypeDeleteView.as_view(), name='delete_oer_type'),

]
