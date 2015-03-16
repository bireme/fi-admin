from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from utils.admin import GenericAdmin

class SuggestResourceAdmin(GenericAdmin):
    model = SuggestResource
    date_hierarchy = 'created_time'
    list_display = ('id','title', 'status')
    search_fields = ['id', 'title']

admin.site.register(SuggestResource, SuggestResourceAdmin)
