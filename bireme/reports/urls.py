from django.urls import re_path

from reports.views import *

app_name = 'reports'

urlpatterns = [
    # Reports
    re_path(r'^/?$', ReportsListView.as_view(), name='list_reports'),
]
