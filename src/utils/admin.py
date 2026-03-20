from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from utils.models import *

class GenericAdmin(admin.ModelAdmin):
    exclude = ()

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'updater') and hasattr(obj, 'creator'):
            if change:
                obj.updated_by = request.user
            else:
                obj.created_by = request.user
                obj.updated_by = request.user
        obj.save()


class CountryLocalAdmin(admin.TabularInline):
    model = CountryLocal
    extra = 0

class CountryAdmin(GenericAdmin):
    model = Country
    inlines = [CountryLocalAdmin,]
    search_fields = list_display = ['code', 'name']
    list_filter = ('LA_Caribbean',)

class ContentTypeAdmin(GenericAdmin):
    model = ContentType
    list_display = ['pk', 'name']
    search_fields = ['name',]

class LogEntryAdmin(GenericAdmin):
    model = LogEntry
    #list_display = ['pk', 'name']
    #search_fields = ['name',]


class AuxCodeLocalAdmin(admin.TabularInline):
    model = AuxCodeLocal
    extra = 0

class AuxCodeAdmin(GenericAdmin):
    model = AuxCode
    inlines = [AuxCodeLocalAdmin,]
    search_fields = list_display = ['code', 'field', 'label']
    list_filter = ('field',)


admin.site.register(Country, CountryAdmin)
admin.site.register(ContentType, ContentTypeAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(AuxCode, AuxCodeAdmin)
