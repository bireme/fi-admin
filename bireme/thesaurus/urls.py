#! coding: utf-8
from django.conf.urls import patterns, include, url

from views import *

urlpatterns = [

    # Descriptors
    url(r'^descriptors/?$', DescListView.as_view(), name='list_descriptor'),
    url(r'^descriptors/new/?$', DescCreateView.as_view(), name='create_descriptor'),
    url(r'^descriptors/edit/(?P<pk>\d+)/?$', DescUpdateView.as_view(), name='edit_descriptor'),
    url(r'^descriptors/delete/(?P<pk>\d+)/?$', DescDeleteView.as_view(), name='delete_descriptor'),

    # url(r'^descriptors/edit/relation/(?P<pk>\d+)/?$', DescConceptRelationView.as_view(), name='edit_concept_relation_descriptor'),


    # Qualifiers
    url(r'^qualifiers/?$', QualifListView.as_view(), name='list_qualifier'),
    url(r'^qualifiers/new/?$', QualifCreateView.as_view(), name='create_qualifier'),
    url(r'^qualifiers/edit/(?P<pk>\d+)/?$', QualifUpdateView.as_view(), name='edit_qualifier'),
    url(r'^qualifiers/delete/(?P<pk>\d+)/?$', QualifDeleteView.as_view(), name='delete_qualifier'),

]

