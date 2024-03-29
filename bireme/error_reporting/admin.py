from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from error_reporting.models import *
from utils.admin import GenericAdmin


class ErrorReportAdmin(GenericAdmin):
    model = ErrorReport
    list_display = ('code', 'description', 'status', 'created_time')
    extra = 0


admin.site.register(ErrorReport, ErrorReportAdmin)
