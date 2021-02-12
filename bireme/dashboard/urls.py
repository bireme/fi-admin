from django.urls import path, re_path

from dashboard import views as dashboard_views

app_name = 'dashboard'

urlpatterns = [
    re_path(r'^$', dashboard_views.widgets, name='widgets'),

    # Dashboard widgets
    re_path(r'^dashboard/last_actions/$', dashboard_views.last_actions, name='last_actions'),
    re_path(r'^dashboard/changed_by_others/(?P<review_type>\w{0,15})/$', dashboard_views.changed_by_others, name='changed_by_others'),
    re_path(r'^dashboard/llxp_indexed_by_cc/$', dashboard_views.llxp_indexed_by_cc, name='llxp_indexed_by_cc'),

]
