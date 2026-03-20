from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from log.models import LogReview

class LogReviewAdmin(admin.ModelAdmin):
    model = LogReview
    date_hierarchy = 'created_time'
    raw_id_fields = ('log', )

admin.site.register(LogReview, LogReviewAdmin)
