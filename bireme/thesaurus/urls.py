#! coding: utf-8
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = [

    # Descriptors -------------------------------------------------------------------------------------------
    url(r'^descriptors/?$', DescListView.as_view(), name='list_descriptor'),
    url(r'^descriptors/new/?$', DescCreateView.as_view(), name='create_descriptor'),
    url(r'^descriptors/edit/(?P<pk>\d+)/?$', DescUpdateView.as_view(), name='edit_descriptor'),
    url(r'^descriptors/delete/(?P<pk>\d+)/?$', DescDeleteView.as_view(), name='delete_descriptor'),

    # TermListDesc - create/update/delete
    url(r'^descriptors/new/term/?$', TermListDescCreateView.as_view(), name='create_termlistdesc'),
    url(r'^descriptors/edit/term/(?P<pk>[\w-]+)$', TermListDescEditView.as_view(), name='edit_termlistdesc'),
    url(r'^descriptors/delete/term/(?P<pk>\d+)/?$', TermListDescDeleteView.as_view(), name='delete_termlistdesc'),

    # Qualifiers --------------------------------------------------------------------------------------------
    url(r'^qualifiers/?$', QualifListView.as_view(), name='list_qualifier'),
    url(r'^qualifiers/new/?$', QualifCreateView.as_view(), name='create_qualifier'),
    url(r'^qualifiers/edit/(?P<pk>\d+)/?$', QualifUpdateView.as_view(), name='edit_qualifier'),
    url(r'^qualifiers/delete/(?P<pk>\d+)/?$', QualifDeleteView.as_view(), name='delete_qualifier'),

    # TermListQualif - create/update/delete
    url(r'^qualifiers/new/term/?$', TermListQualifCreateView.as_view(), name='create_termlistqualif'),
    url(r'^qualifiers/edit/term/(?P<pk>[\w-]+)$', TermListQualifEditView.as_view(), name='edit_termlistqualif'),
    url(r'^qualifiers/delete/term/(?P<pk>\d+)/?$', TermListQualifDeleteView.as_view(), name='delete_termlistqualif'),


]

