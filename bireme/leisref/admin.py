from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes import generic

from models import *
from main.models import Descriptor, Keyword, ResourceThematic
from attachments.models import Attachment
from utils.admin import GenericAdmin


class DescriptorAdmin(generic.GenericTabularInline):
    model = Descriptor
    exclude = ('status', 'code')
    extra = 1


class ThematicAreaAdmin(generic.GenericTabularInline):
    model = ResourceThematic
    exclude = ('status',)
    extra = 1


class ActRelationshipAdmin(admin.TabularInline):
    model = ActRelationship
    fk_name = 'act_related'
    extra = 1


class AttachmentAdmin(generic.GenericTabularInline):
    model = Attachment
    exclude = ('short_url',)
    extra = 1


class ActURLAdmin(admin.TabularInline):
    model = ActURL
    extra = 1


class ActAdmin(GenericAdmin):
    model = Act
    date_hierarchy = 'created_time'
    list_display = ('id', '__unicode__', 'created_by', 'status')
    search_fields = ['id', '__unicode__']
    inlines = [ActRelationshipAdmin, ActURLAdmin, AttachmentAdmin, DescriptorAdmin, ThematicAreaAdmin, ]

admin.site.register(Act, ActAdmin)
admin.site.register(ActType)
admin.site.register(ActScope)
admin.site.register(ActCountryRegion)
admin.site.register(ActOrganIssuer)
admin.site.register(ActRelationType)
admin.site.register(ActSource)
