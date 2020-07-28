from django.urls import path, re_path

from leisref.views import *

urlpatterns = [
    # LeisRef
    path('', LeisRefListView.as_view(), name='list_legislation'),
    re_path(r'^act-related/?$', LeisRefActListView.as_view(), name='act_related'),
    re_path(r'^new/?$', ActCreateView.as_view(), name='create_legislation'),
    re_path(r'^edit/(?P<pk>\d+)/?$', ActUpdateView.as_view(), name='edit_legislation'),
    re_path(r'^delete/(?P<pk>\d+)/?$', ActDeleteView.as_view(), name='delete_legislation'),
    re_path(r'^add-related-act/', add_related_act, name='add_related_act'),

    re_path(r'^context-lists/(?P<region_id>\d+)/?$', context_lists, name='get_context_lists'),
    re_path(r'^check-dup/(?P<act_type>\d+)/(?P<act_number>\w+)?$', check_duplication, name='act_check_duplication'),

    # Aux Country/Region
    re_path(r'^aux-country-region/?$', CountryRegionListView.as_view(), name='list_country_region'),
    re_path(r'^aux-country-region/new/?$', CountryRegionCreateView.as_view(), name='create_country_region'),
    re_path(r'^aux-country-region/edit/(?P<pk>\d+)/?$', CountryRegionUpdateView.as_view(), name='edit_country_region'),
    re_path(r'^aux-country-region/delete/(?P<pk>\d+)/?$', CountryRegionDeleteView.as_view(), name='delete_country_region'),

    # Aux Act Scope
    re_path(r'^aux-act-scope/?$', ActScopeListView.as_view(), name='list_act_scope'),
    re_path(r'^aux-act-scope/new/?$', ActScopeCreateView.as_view(), name='create_act_scope'),
    re_path(r'^aux-act-scope/edit/(?P<pk>\d+)/?$', ActScopeUpdateView.as_view(), name='edit_act_scope'),
    re_path(r'^aux-act-scope/delete/(?P<pk>\d+)/?$', ActScopeDeleteView.as_view(), name='delete_act_scope'),

    # Aux Act Type
    re_path(r'^aux-act-type/?$', ActTypeListView.as_view(), name='list_act_type'),
    re_path(r'^aux-act-type/new/?$', ActTypeCreateView.as_view(), name='create_act_type'),
    re_path(r'^aux-act-type/edit/(?P<pk>\d+)/?$', ActTypeUpdateView.as_view(), name='edit_act_type'),
    re_path(r'^aux-act-type/delete/(?P<pk>\d+)/?$', ActTypeDeleteView.as_view(), name='delete_act_type'),

    # Aux Act Organ Issuer
    re_path(r'^aux-act-organ/?$', ActOrganListView.as_view(), name='list_act_organ'),
    re_path(r'^aux-act-organ/new/?$', ActOrganCreateView.as_view(), name='create_act_organ'),
    re_path(r'^aux-act-organ/edit/(?P<pk>\d+)/?$', ActOrganUpdateView.as_view(), name='edit_act_organ'),
    re_path(r'^aux-act-organ/delete/(?P<pk>\d+)/?$', ActOrganDeleteView.as_view(), name='delete_act_organ'),

    # Aux Act Source
    re_path(r'^aux-act-source/?$', ActSourceListView.as_view(), name='list_act_source'),
    re_path(r'^aux-act-source/new/?$', ActSourceCreateView.as_view(), name='create_act_source'),
    re_path(r'^aux-act-source/edit/(?P<pk>\d+)/?$', ActSourceUpdateView.as_view(), name='edit_act_source'),
    re_path(r'^aux-act-source/delete/(?P<pk>\d+)/?$', ActSourceDeleteView.as_view(), name='delete_act_source'),

    # Aux Act Relation Type
    re_path(r'^aux-act-reltype/?$', ActRelTypeListView.as_view(), name='list_act_reltype'),
    re_path(r'^aux-act-reltype/new/?$', ActRelTypeCreateView.as_view(), name='create_act_reltype'),
    re_path(r'^aux-act-reltype/edit/(?P<pk>\d+)/?$', ActRelTypeUpdateView.as_view(), name='edit_act_reltype'),
    re_path(r'^aux-act-reltype/delete/(?P<pk>\d+)/?$', ActRelTypeDeleteView.as_view(), name='delete_act_reltype'),

    # Aux Act Scope State
    re_path(r'^aux-act-state/?$', ActStateListView.as_view(), name='list_act_state'),
    re_path(r'^aux-act-state/new/?$', ActStateCreateView.as_view(), name='create_act_state'),
    re_path(r'^aux-act-state/edit/(?P<pk>\d+)/?$', ActStateUpdateView.as_view(), name='edit_act_state'),
    re_path(r'^aux-act-state/delete/(?P<pk>\d+)/?$', ActStateDeleteView.as_view(), name='delete_act_state'),

    # Aux Act Scope City
    re_path(r'^aux-act-city/?$', ActCityListView.as_view(), name='list_act_city'),
    re_path(r'^aux-act-city/new/?$', ActCityCreateView.as_view(), name='create_act_city'),
    re_path(r'^aux-act-city/edit/(?P<pk>\d+)/?$', ActCityUpdateView.as_view(), name='edit_act_city'),
    re_path(r'^aux-act-city/delete/(?P<pk>\d+)/?$', ActCityDeleteView.as_view(), name='delete_act_city'),

    # Aux Act collection
    re_path(r'^aux-act-collection/?$', ActCollectionListView.as_view(), name='list_act_collection'),
    re_path(r'^aux-act-collection/new/?$', ActCollectionCreateView.as_view(), name='create_act_collection'),
    re_path(r'^aux-act-collection/edit/(?P<pk>\d+)/?$', ActCollectionUpdateView.as_view(), name='edit_act_collection'),
    re_path(r'^aux-act-collection/delete/(?P<pk>\d+)/?$', ActCollectionDeleteView.as_view(), name='delete_act_collection'),

]
