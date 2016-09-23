from django.conf.urls import url

from views import *

urlpatterns = [
    # LeisRef
    url(r'^/?$', LeisRefListView.as_view(), name='list_legislation'),
    url(r'^list-acts/?$', LeisRefActListView.as_view(), name='list_acts'),
    url(r'^new/?$', ActCreateView.as_view(), name='create_legislation'),
    url(r'^edit/(?P<pk>\d+)/?$', ActUpdateView.as_view(), name='edit_legislation'),
    url(r'^delete/(?P<pk>\d+)/?$', ActDeleteView.as_view(), name='delete_legislation'),

    url(r'^context-lists/(?P<region_id>\d+)/?$', context_lists, name='get_context_lists'),
]
