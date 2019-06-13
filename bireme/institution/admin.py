from django.contrib import admin
from models import *

from utils.admin import GenericAdmin

class AdhesionTermLocalAdmin(admin.TabularInline):
    model = AdhesionTermLocal
    extra = 1


class AdhesionTermAdmin(admin.ModelAdmin):
    model = AdhesionTerm
    inlines = [AdhesionTermLocalAdmin, ]


class ServiceProductLocalAdmin(admin.TabularInline):
    model = ServiceProductLocal
    extra = 1

class ServiceProductAdmin(admin.ModelAdmin):
    model = ServiceProduct
    inlines = [ServiceProductLocalAdmin, ]


# Django Admin models register
admin.site.register(AdhesionTerm, AdhesionTermAdmin)
admin.site.register(ServiceProduct, ServiceProductAdmin)
