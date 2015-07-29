from django.conf.urls import url

from views import *

urlpatterns = [
    # Reports
    url(r'^/?$', ReportsListView.as_view(), name='list_reports'),
]
