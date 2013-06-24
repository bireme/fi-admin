from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from utils.admin import GenericAdmin


class TopicLocalAdmin(admin.TabularInline):
    model = TopicLocal
    extra = 0

class TopicAdmin(GenericAdmin):
    model = Topic
    inlines = [TopicLocalAdmin,]

class SourceTypeLocalAdmin(admin.TabularInline):
    model = SourceTypeLocal
    extra = 0

class SourceTypeAdmin(GenericAdmin):
    model = SourceType
    inlines = [SourceTypeLocalAdmin,]


class ResourceAdmin(GenericAdmin):
    model = Resource

admin.site.register(Resource, ResourceAdmin)
admin.site.register(SourceType, SourceTypeAdmin)
admin.site.register(Topic, TopicAdmin)

