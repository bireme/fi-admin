from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from utils.admin import GenericAdmin


class ErrorReportAdmin(GenericAdmin):
    model = ErrorReport
    extra = 0


admin.site.register(ErrorReport, ErrorReportAdmin)
