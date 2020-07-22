from django.urls import re_path

from institution.views import *

urlpatterns = [
    # Institution
    re_path(r'^/?$', InstListView.as_view(), name='list_institution'),
    re_path(r'^new/?$', InstCreateView.as_view(), name='create_institution'),
    re_path(r'^edit/(?P<pk>\d+)/?$', InstUpdateView.as_view(), name='edit_institution'),
    re_path(r'^delete/(?P<pk>\d+)/?$', InstDeleteView.as_view(), name='delete_institution'),

    re_path(r'^unit/?$', UnitListView.as_view(), name='list_unit'),
    re_path(r'^add-unit/', add_unit, name='add_unit'),

    re_path(r'^adhesionterm/(?P<institution_id>\d+)/?$', adhesionterm, name="adhesionterm"),
]
