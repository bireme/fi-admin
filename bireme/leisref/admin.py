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


class ActTypeLocalAdmin(admin.TabularInline):
    model = ActTypeLocal
    extra = 1


class ActTypeAdmin(GenericAdmin):
    model = ActType
    inlines = [ActTypeLocalAdmin, ]


class ActScopeLocalAdmin(admin.TabularInline):
    model = ActScopeLocal
    extra = 1


class ActScopeAdmin(GenericAdmin):
    model = ActScope
    inlines = [ActScopeLocalAdmin, ]


class ActRelationTypeLocalAdmin(admin.TabularInline):
    model = ActRelationTypeLocal
    extra = 1


class ActRelationTypeAdmin(GenericAdmin):
    model = ActRelationType
    inlines = [ActRelationTypeLocalAdmin, ]


class ActOrganIssuerLocalAdmin(admin.TabularInline):
    model = ActOrganIssuerLocal
    extra = 1


class ActOrganIssuerAdmin(GenericAdmin):
    model = ActOrganIssuer
    inlines = [ActOrganIssuerLocalAdmin, ]


class ActAdmin(GenericAdmin):
    model = Act
    date_hierarchy = 'created_time'
    list_display = ('id', '__unicode__', 'created_by', 'status')
    search_fields = ['id', '__unicode__']
    inlines = [ActRelationshipAdmin, ActURLAdmin, AttachmentAdmin, DescriptorAdmin, ThematicAreaAdmin, ]

admin.site.register(Act, ActAdmin)
admin.site.register(ActType, ActTypeAdmin)
admin.site.register(ActScope, ActScopeAdmin)
admin.site.register(ActCountryRegion)
admin.site.register(ActOrganIssuer, ActOrganIssuerAdmin)
admin.site.register(ActRelationType, ActRelationTypeAdmin)
admin.site.register(ActRelationship)
admin.site.register(ActSource)
