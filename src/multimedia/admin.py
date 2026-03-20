from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from utils.admin import GenericAdmin

from multimedia.models import *

class MediaTypeLocalAdmin(admin.TabularInline):
    model = MediaTypeLocal
    extra = 1

class MediaTypeAdmin(GenericAdmin):
    model = MediaType
    inlines = [MediaTypeLocalAdmin, ]


class MediaAdmin(admin.ModelAdmin):
    model = Media
    date_hierarchy = 'created_time'
    raw_id_fields = ('media_collection', )
    list_display = ('id','title', 'status', 'created_by')
    list_filter = ('status', 'media_type__name', 'language__name', 'cooperative_center_code')

admin.site.register(Media, MediaAdmin)
admin.site.register(MediaType, MediaTypeAdmin)
