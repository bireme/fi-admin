from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from utils.admin import GenericAdmin


class ThematicAreaLocalAdmin(admin.TabularInline):
    model = ThematicAreaLocal
    extra = 0

class ThematicAreaAdmin(GenericAdmin):
    model = ThematicArea
    inlines = [ThematicAreaLocalAdmin,]

class SourceTypeLocalAdmin(admin.TabularInline):
    model = SourceTypeLocal
    extra = 0

class SourceTypeAdmin(GenericAdmin):
    model = SourceType
    inlines = [SourceTypeLocalAdmin,]

class DescriptorAdmin(admin.TabularInline):
    model = Descriptor
    extra = 1


class ResourceThematicAdmin(admin.TabularInline):
    model = ResourceThematic
    extra = 1


class ResourceAdmin(GenericAdmin):
    model = Resource
    inlines = [DescriptorAdmin, ResourceThematicAdmin]

admin.site.register(Resource, ResourceAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(ThematicArea, ThematicAreaAdmin)
admin.site.register(Descriptor)
