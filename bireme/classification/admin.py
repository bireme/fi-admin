from django.contrib import admin

from models import *


class CollectionLocalAdmin(admin.TabularInline):
    model = CollectionLocal
    extra = 1


class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    inlines = [CollectionLocalAdmin, ]


admin.site.register(Collection, CollectionAdmin)
