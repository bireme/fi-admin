from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *

class MediaAdmin(admin.ModelAdmin):
    model = Media
    date_hierarchy = 'created_time'
    raw_id_fields = ('media_collection', )
    list_display = ('id','title', 'status', 'created_by')
    
admin.site.register(Media, MediaAdmin)
