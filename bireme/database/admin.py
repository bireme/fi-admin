from django.contrib import admin
from utils.admin import GenericAdmin

from database.models import *

class DatabaseLocalAdmin(admin.TabularInline):
    model = DatabaseLocal
    extra = 0


class DatabaseAdmin(GenericAdmin):
    model = Database
    inlines = [DatabaseLocalAdmin, ]
    search_fields = list_display = ['acronym', 'name']
    list_filter = ('regional_index', 'network_index', 'cc_index')


admin.site.register(Database, DatabaseAdmin)
