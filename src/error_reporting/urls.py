from django.urls import re_path

from error_reporting import views as error_reporting_views

app_name = 'error_reporting'

urlpatterns = [
    re_path(r'^error-reporting/?$', error_reporting_views.list_error_report, name='list_error_report'),
    re_path(r'^error-reporting/new/?$', error_reporting_views.create_error_report, name='create_error_report'),
    re_path(r'^error-reporting/edit/(?P<report_id>\d+)/?$', error_reporting_views.edit_error_report, name='edit_error_report'),
    # External error report
    re_path(r'^report-error/?$', error_reporting_views.external_error_report, name='external_error_report'),
]
