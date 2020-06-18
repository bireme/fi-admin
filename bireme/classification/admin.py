from django.contrib import admin

from models import *


class CollectionLocalAdmin(admin.TabularInline):
    model = CollectionLocal
    extra = 1


class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    list_display = ('community_collection_path', 'country')
    inlines = [CollectionLocalAdmin, ]
    ordering = ('parent',)


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Relationship)
