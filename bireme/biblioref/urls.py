from django.urls import re_path

from biblioref.views import *

urlpatterns = [
    re_path(r'^/?$', BiblioRefListView.as_view(), name='list_biblioref'),
    re_path(r'^type/?$', SelectDocumentTypeView.as_view(), name='select_biblioref_type'),
    re_path(r'^sources?$', BiblioRefListSourceView.as_view(), name='list_biblioref_sources'),
    re_path(r'^analytics?$', BiblioRefListAnalyticView.as_view(), name='list_biblioref_analytics'),
    re_path(r'^new-source/?$', BiblioRefSourceCreateView.as_view(), name='create_biblioref_source'),
    re_path(r'^new-analytic/?$', BiblioRefAnalyticCreateView.as_view(), name='create_biblioref_analytic'),
    re_path(r'^edit-source/(?P<pk>\d+)/?$', BiblioRefSourceUpdateView.as_view(), name='edit_biblioref_source'),
    re_path(r'^edit-analytic/(?P<pk>\d+)/?$', BiblioRefAnaliticUpdateView.as_view(), name='edit_biblioref_analytic'),
    re_path(r'^delete/(?P<pk>\d+)/?$', BiblioRefDeleteView.as_view(), name='delete_biblioref'),

    re_path(r'^duplicates/(?P<reference_id>\d+)/', view_duplicates, name='view_duplicates'),
]
