from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin

from main.models import Descriptor, Keyword, ThematicArea
from error_reporting.models import ErrorReport
from utils.admin import GenericAdmin

from events.models import *

class DescriptorAdmin(GenericTabularInline):
    model = Descriptor
    extra = 1


class KeywordAdmin(GenericTabularInline):
    model = Keyword
    extra = 1


class ThematicAreaAdmin(GenericTabularInline):
    model = ResourceThematic
    extra = 1


class EventAdmin(GenericAdmin):
    model = Event
    date_hierarchy = 'created_time'
    list_display = ('id', 'title', 'created_by', 'status')
    search_fields = ['id', 'title']
    list_filter = ('status', 'official_language__language', 'event_type__name',
                   'thematics__thematic_area', 'cooperative_center_code')
    inlines = [DescriptorAdmin, KeywordAdmin, ThematicAreaAdmin, ]

admin.site.register(Event, EventAdmin)
