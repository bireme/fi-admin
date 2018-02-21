from django.conf.urls import url

from views import *

urlpatterns = [
    # Institution
    url(r'^/?$', InstListView.as_view(), name='list_institution'),
    url(r'^new/?$', InstCreateView.as_view(), name='create_institution'),
    url(r'^edit/(?P<pk>\d+)/?$', InstUpdateView.as_view(), name='edit_institution'),
    url(r'^delete/(?P<pk>\d+)/?$', InstDeleteView.as_view(), name='delete_institution'),
]
