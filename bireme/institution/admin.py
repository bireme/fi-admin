from django.contrib import admin
from models import *

from utils.admin import GenericAdmin

class TypeLocalAdmin(admin.TabularInline):
    model = TypeLocal
    extra = 0


class TypeAdmin(GenericAdmin):
    model = Type
    inlines = [TypeLocalAdmin, ]

# Register your models here.
admin.site.register(Type, TypeAdmin)
