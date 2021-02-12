from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin

from main.models import *
from error_reporting.models import ErrorReport
from utils.admin import GenericAdmin


class ThematicAreaLocalAdmin(admin.TabularInline):
    model = ThematicAreaLocal
    extra = 0


class ThematicAreaAdmin(GenericAdmin):
    model = ThematicArea
    list_display = ('id', 'name', 'acronym')
    search_fields = ['name', 'acronym']
    inlines = [ThematicAreaLocalAdmin, ]


class SourceTypeLocalAdmin(admin.TabularInline):
    model = SourceTypeLocal
    extra = 0


class SourceTypeAdmin(GenericAdmin):
    model = SourceType
    inlines = [SourceTypeLocalAdmin, ]


class SourceLanguageLocalAdmin(admin.TabularInline):
    model = SourceLanguageLocal
    extra = 0


class SourceLanguageAdmin(GenericAdmin):
    model = SourceType
    inlines = [SourceLanguageLocalAdmin, ]


class DescriptorAdmin(GenericTabularInline):
    model = Descriptor
    extra = 1


class KeywordAdmin(GenericTabularInline):
    model = Keyword
    extra = 1


class ErrorReportAdmin(GenericTabularInline):
    model = ErrorReport
    extra = 1


class ThematicAreaAdmin(GenericTabularInline):
    model = ResourceThematic
    extra = 1


class ResourceAdmin(GenericAdmin):
    model = Resource
    date_hierarchy = 'created_time'
    list_display = ('id', 'title', 'link', 'created_by', 'status')
    search_fields = ['id', 'title']
    list_filter = ('status', 'source_language__language', 'source_type__name',
                   'thematics__thematic_area', 'cooperative_center_code')
    inlines = [DescriptorAdmin, KeywordAdmin, ThematicAreaAdmin, ErrorReportAdmin, ]

admin.site.register(Resource, ResourceAdmin)
admin.site.register(SourceLanguage, SourceLanguageAdmin)
admin.site.register(ThematicArea)
