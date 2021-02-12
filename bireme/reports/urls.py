from django.urls import path

from reports.views import *

app_name = 'reports'

urlpatterns = [
    # Reports
    path('', ReportsListView.as_view(), name='list_reports'),
]
