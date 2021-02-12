from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from multimedia.models import *

class MediaAdmin(admin.ModelAdmin):
    model = Media
    date_hierarchy = 'created_time'
    raw_id_fields = ('media_collection', )
    list_display = ('id','title', 'status', 'created_by')
    list_filter = ('status', 'media_type__name', 'language__name', 'cooperative_center_code')

admin.site.register(Media, MediaAdmin)
