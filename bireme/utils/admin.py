from django.contrib import admin
from models import *

class GenericAdmin(admin.ModelAdmin):
    exclude = ()

    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'updater') and hasattr(obj, 'creator'):
            if change:
                obj.updater = request.user
            else:
                obj.creator = request.user
                obj.updater = request.user
        obj.save()


class CountryLocalAdmin(admin.TabularInline):
    model = CountryLocal
    extra = 0

class CountryAdmin(GenericAdmin):
    model = Country
    inlines = [CountryLocalAdmin,]
    search_fields = list_display = ['code', 'name']

admin.site.register(Country, CountryAdmin)