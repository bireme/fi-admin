from django.contrib import admin

from models import *


class TermLocalAdmin(admin.TabularInline):
    model = TermLocal
    extra = 1


class TermAdmin(admin.ModelAdmin):
    model = Term
    inlines = [TermLocalAdmin, ]


admin.site.register(Type)
admin.site.register(Term, TermAdmin)
