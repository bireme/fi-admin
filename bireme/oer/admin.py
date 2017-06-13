from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.contenttypes import generic

from models import *
from utils.admin import GenericAdmin


class TypeLocalAdmin(admin.TabularInline):
    model = TypeLocal
    extra = 1


class TypeAdmin(GenericAdmin):
    model = Type
    inlines = [TypeLocalAdmin, ]


class LicenseLocalAdmin(admin.TabularInline):
    model = LicenseLocal
    extra = 1


class LicenseAdmin(GenericAdmin):
    model = License
    inlines = [LicenseLocalAdmin, ]


class CourseTypeLocalAdmin(admin.TabularInline):
    model = CourseTypeLocal
    extra = 1


class CourseTypeAdmin(GenericAdmin):
    model = CourseType
    inlines = [CourseTypeLocalAdmin, ]


class TecResourceTypeLocalAdmin(admin.TabularInline):
    model = TecResourceTypeLocal
    extra = 1


class TecResourceTypeAdmin(GenericAdmin):
    model = TecResourceType
    inlines = [TecResourceTypeLocalAdmin, ]


class FormatLocalAdmin(admin.TabularInline):
    model = FormatLocal
    extra = 1


class FormatAdmin(GenericAdmin):
    model = Format
    inlines = [FormatLocalAdmin, ]


class InteractivityTypeLocalAdmin(admin.TabularInline):
    model = InteractivityTypeLocal
    extra = 1


class InteractivityTypeAdmin(GenericAdmin):
    model = InteractivityType
    inlines = [InteractivityTypeLocalAdmin, ]


class DifficultyLocalAdmin(admin.TabularInline):
    model = DifficultyLocal
    extra = 1


class DifficultyAdmin(GenericAdmin):
    model = Difficulty
    inlines = [DifficultyLocalAdmin, ]


class AudienceLocalAdmin(admin.TabularInline):
    model = AudienceLocal
    extra = 1


class AudienceAdmin(GenericAdmin):
    model = Audience
    inlines = [AudienceLocalAdmin, ]


class RelationshipAdmin(admin.TabularInline):
    model = Relationship
    fk_name = 'oer_related'
    extra = 1


class RelationTypeLocalAdmin(admin.TabularInline):
    model = RelationTypeLocal
    extra = 1


class RelationTypeAdmin(GenericAdmin):
    model = RelationType
    inlines = [RelationTypeLocalAdmin, ]


class LearningContextLocalAdmin(admin.TabularInline):
    model = LearningContextLocal
    extra = 1


class LearningContextAdmin(GenericAdmin):
    model = LearningContext
    inlines = [LearningContextLocalAdmin, ]


class LearningResourceTypeLocalAdmin(admin.TabularInline):
    model = LearningResourceTypeLocal
    extra = 1


class LearningResourceTypeAdmin(GenericAdmin):
    model = LearningResourceType
    inlines = [LearningResourceTypeLocalAdmin, ]


admin.site.register(Type, TypeAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(CourseType, CourseTypeAdmin)
admin.site.register(TecResourceType, TecResourceTypeAdmin)
admin.site.register(Format, FormatAdmin)
admin.site.register(InteractivityType, InteractivityTypeAdmin)
admin.site.register(Difficulty, DifficultyAdmin)
admin.site.register(Audience, AudienceAdmin)
admin.site.register(RelationType, RelationTypeAdmin)
admin.site.register(LearningContext, LearningContextAdmin)
admin.site.register(LearningResourceType, LearningResourceTypeAdmin)
