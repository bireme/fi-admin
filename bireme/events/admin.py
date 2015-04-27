from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from error_reporting.models import ErrorReport
from utils.admin import GenericAdmin

class EventAdmin(GenericAdmin):
    model = Event
    date_hierarchy = 'created_time'
    list_display = ('id','title', 'created_by', 'status')
    search_fields = ['id', 'title']
    list_filter = ('status', 'official_language__language', 'event_type__name', 'thematics__thematic_area', 'cooperative_center_code')

admin.site.register(Event, EventAdmin)
