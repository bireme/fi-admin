from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *

admin.site.register(Media)
admin.site.register(MediaType)
admin.site.register(MediaTypeLocal)
