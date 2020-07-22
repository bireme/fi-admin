from django.contrib import admin
from institution.models import *

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


class TypeLocalAdmin(admin.TabularInline):
    model = TypeLocal
    extra = 1


class TypeAdmin(GenericAdmin):
    model = Type
    inlines = [TypeLocalAdmin,]


class CategoryLocalAdmin(admin.TabularInline):
    model = CategoryLocal
    extra = 1


class CategoryAdmin(GenericAdmin):
    model = Category
    inlines = [CategoryLocalAdmin,]


class UnitAdmin(GenericAdmin):
    model = Unit
    search_fields = ['name', 'acronym']
    list_filter = ('country',)


# Django Admin models register
admin.site.register(AdhesionTerm, AdhesionTermAdmin)
admin.site.register(ServiceProduct, ServiceProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(Unit, UnitAdmin)
