from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *

class MediaAdmin(admin.ModelAdmin):
    raw_id_fields = ('media_collection', )

admin.site.register(Media, MediaAdmin)
admin.site.register(MediaType)
admin.site.register(MediaTypeLocal)

admin.site.register(MediaCollection)
