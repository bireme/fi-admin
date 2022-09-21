from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from utils.admin import GenericAdmin

from related.models import *

class ResourceTypeLocalAdmin(admin.TabularInline):
    model = LinkedResourceTypeLocal
    extra = 1


class ResourceTypeAdmin(GenericAdmin):
    model = LinkedResourceType
    list_display = ('id', 'field', 'name', 'order')
    inlines = [ResourceTypeLocalAdmin, ]


admin.site.register(LinkedResourceType, ResourceTypeAdmin)
