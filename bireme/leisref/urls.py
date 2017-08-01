from django.conf.urls import url

from views import *

urlpatterns = [
    # LeisRef
    url(r'^/?$', LeisRefListView.as_view(), name='list_legislation'),
    url(r'^act-related/?$', LeisRefActListView.as_view(), name='act_related'),
    url(r'^new/?$', ActCreateView.as_view(), name='create_legislation'),
    url(r'^edit/(?P<pk>\d+)/?$', ActUpdateView.as_view(), name='edit_legislation'),
    url(r'^delete/(?P<pk>\d+)/?$', ActDeleteView.as_view(), name='delete_legislation'),
    url(r'^add-related-act/', add_related_act, name='add_related_act'),
    url(r'^context-lists/(?P<region_id>\d+)/?$', context_lists, name='get_context_lists'),

    # Aux Country/Region
    url(r'^aux-country-region/?$', CountryRegionListView.as_view(), name='list_country_region'),
    url(r'^aux-country-region/new/?$', CountryRegionCreateView.as_view(), name='create_country_region'),
    url(r'^aux-country-region/edit/(?P<pk>\d+)/?$', CountryRegionUpdateView.as_view(), name='edit_country_region'),
    url(r'^aux-country-region/delete/(?P<pk>\d+)/?$', CountryRegionDeleteView.as_view(), name='delete_country_region'),

    # Aux Act Scope
    url(r'^aux-act-scope/?$', ActScopeListView.as_view(), name='list_act_scope'),
    url(r'^aux-act-scope/new/?$', ActScopeCreateView.as_view(), name='create_act_scope'),
    url(r'^aux-act-scope/edit/(?P<pk>\d+)/?$', ActScopeUpdateView.as_view(), name='edit_act_scope'),
    url(r'^aux-act-scope/delete/(?P<pk>\d+)/?$', ActScopeDeleteView.as_view(), name='delete_act_scope'),

    # Aux Act Type
    url(r'^aux-act-type/?$', ActTypeListView.as_view(), name='list_act_type'),
    url(r'^aux-act-type/new/?$', ActTypeCreateView.as_view(), name='create_act_type'),
    url(r'^aux-act-type/edit/(?P<pk>\d+)/?$', ActTypeUpdateView.as_view(), name='edit_act_type'),
    url(r'^aux-act-type/delete/(?P<pk>\d+)/?$', ActTypeDeleteView.as_view(), name='delete_act_type'),

    # Aux Act Organ Issuer
    url(r'^aux-act-organ/?$', ActOrganListView.as_view(), name='list_act_organ'),
    url(r'^aux-act-organ/new/?$', ActOrganCreateView.as_view(), name='create_act_organ'),
    url(r'^aux-act-organ/edit/(?P<pk>\d+)/?$', ActOrganUpdateView.as_view(), name='edit_act_organ'),
    url(r'^aux-act-organ/delete/(?P<pk>\d+)/?$', ActOrganDeleteView.as_view(), name='delete_act_organ'),

    # Aux Act Source
    url(r'^aux-act-source/?$', ActSourceListView.as_view(), name='list_act_source'),
    url(r'^aux-act-source/new/?$', ActSourceCreateView.as_view(), name='create_act_source'),
    url(r'^aux-act-source/edit/(?P<pk>\d+)/?$', ActSourceUpdateView.as_view(), name='edit_act_source'),
    url(r'^aux-act-source/delete/(?P<pk>\d+)/?$', ActSourceDeleteView.as_view(), name='delete_act_source'),

    # Aux Act Relation Type
    url(r'^aux-act-reltype/?$', ActRelTypeListView.as_view(), name='list_act_reltype'),
    url(r'^aux-act-reltype/new/?$', ActRelTypeCreateView.as_view(), name='create_act_reltype'),
    url(r'^aux-act-reltype/edit/(?P<pk>\d+)/?$', ActRelTypeUpdateView.as_view(), name='edit_act_reltype'),
    url(r'^aux-act-reltype/delete/(?P<pk>\d+)/?$', ActRelTypeDeleteView.as_view(), name='delete_act_reltype'),

    # Aux Act Scope State
    url(r'^aux-act-state/?$', ActStateListView.as_view(), name='list_act_state'),
    url(r'^aux-act-state/new/?$', ActStateCreateView.as_view(), name='create_act_state'),
    url(r'^aux-act-state/edit/(?P<pk>\d+)/?$', ActStateUpdateView.as_view(), name='edit_act_state'),
    url(r'^aux-act-state/delete/(?P<pk>\d+)/?$', ActStateDeleteView.as_view(), name='delete_act_state'),

    # Aux Act Scope City
    url(r'^aux-act-city/?$', ActCityListView.as_view(), name='list_act_city'),
    url(r'^aux-act-city/new/?$', ActCityCreateView.as_view(), name='create_act_city'),
    url(r'^aux-act-city/edit/(?P<pk>\d+)/?$', ActCityUpdateView.as_view(), name='edit_act_city'),
    url(r'^aux-act-city/delete/(?P<pk>\d+)/?$', ActCityDeleteView.as_view(), name='delete_act_city'),

]
