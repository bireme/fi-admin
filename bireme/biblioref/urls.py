from django.conf.urls import url
from views import *

urlpatterns = [

    # Bibliographic Record
    url(r'^/?$', BiblioRefListView.as_view(), name='list_biblioref'),
    url(r'^type/?$', SelectDocumentTypeView.as_view(), name='select_biblioref_type'),
    url(r'^sources?$', BiblioRefListSourceView.as_view(), name='list_biblioref_sources'),
    url(r'^analytics?$', BiblioRefListAnalyticView.as_view(), name='list_biblioref_analytics'),
    url(r'^new-source/?$', BiblioRefSourceCreateView.as_view(), name='create_biblioref_source'),
    url(r'^new-analytic/?$', BiblioRefAnalyticCreateView.as_view(), name='create_biblioref_analytic'),
    url(r'^edit-source/(?P<pk>\d+)/?$', BiblioRefSourceUpdateView.as_view(), name='edit_biblioref_source'),
    url(r'^edit-analytic/(?P<pk>\d+)/?$', BiblioRefAnaliticUpdateView.as_view(), name='edit_biblioref_analytic'),
    url(r'^delete/(?P<pk>\d+)/?$', BiblioRefDeleteView.as_view(), name='delete_biblioref'),

    url(r'^duplicates/(?P<reference_id>\d+)/', view_duplicates, name='view_duplicates'),
]
