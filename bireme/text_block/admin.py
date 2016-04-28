from django.contrib import admin
from models import *


class TextBlockLocalAdmin(admin.TabularInline):
    model = TextBlockLocal
    extra = 2


class TextBlockAdmin(admin.ModelAdmin):
    model = TextBlock
    inlines = [TextBlockLocalAdmin, ]


admin.site.register(TextBlock, TextBlockAdmin)
