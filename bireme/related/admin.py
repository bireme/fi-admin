from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from utils.admin import GenericAdmin

from related.models import *


class ResearchDataTypeLocalAdmin(admin.TabularInline):
    model = ResearchDataTypeLocal
    extra = 1


class ResearchDataTypeAdmin(GenericAdmin):
    model = ResearchDataType
    inlines = [ResearchDataTypeLocalAdmin, ]


class ResourceTypeLocalAdmin(admin.TabularInline):
    model = ResourceTypeLocal
    extra = 1


class ResourceTypeAdmin(GenericAdmin):
    model = ResourceType
    inlines = [ResourceTypeLocalAdmin, ]



admin.site.register(ResearchDataType, ResearchDataTypeAdmin)
admin.site.register(ResourceType, ResourceTypeAdmin)
