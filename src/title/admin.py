from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from title.models import *

@admin.register(Mask)
class MaskAdmin(admin.ModelAdmin):
    readonly_fields = ["mask"]

models = [Title, TitleVariance, BVSSpecialty, IndexRange, Audit, OnlineResources, OwnerList, IndexCode, Users, Issue, Collection]

admin.site.register(models)
