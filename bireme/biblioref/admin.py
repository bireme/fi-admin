
from django.contrib import admin
from utils.admin import GenericAdmin

from models import *


class ReferenceAlternateIDAdmin(admin.ModelAdmin):
    raw_id_fields = ("reference",)

admin.site.register(ReferenceSource)
admin.site.register(ReferenceAnalytic)
admin.site.register(ReferenceComplement)
admin.site.register(ReferenceAlternateID, ReferenceAlternateIDAdmin)
admin.site.register(ReferenceLocal)
admin.site.register(ReferenceDuplicate)
admin.site.register(Reference)
