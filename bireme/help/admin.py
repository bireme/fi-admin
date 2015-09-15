from django.contrib import admin
from models import *


class HelpLocalAdmin(admin.TabularInline):
    model = HelpLocal
    extra = 2


class HelpAdmin(admin.ModelAdmin):
    model = Help
    inlines = [HelpLocalAdmin, ]


admin.site.register(Help, HelpAdmin)
