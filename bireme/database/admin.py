from django.contrib import admin
from utils.admin import GenericAdmin
from django.core.cache import cache

from database.models import *

class DatabaseLocalAdmin(admin.TabularInline):
    model = DatabaseLocal
    extra = 0


class DatabaseAdmin(GenericAdmin):
    model = Database
    inlines = [DatabaseLocalAdmin, ]
    search_fields = list_display = ['acronym', 'name']
    list_filter = ('regional_index', 'network_index', 'cc_index')
    actions = ['clear_cache']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def clear_cache(self, request, queryset):
        for db in queryset:
            for cache_lang in ['pt-br', 'es', 'en']:
                cache_id = "database-{}-{}".format(cache_lang, db.id)
                try:
                    cache.delete(cache_id)
                except:
                    pass

    clear_cache.short_description = 'Clear cache of selected databases'


admin.site.register(Database, DatabaseAdmin)
