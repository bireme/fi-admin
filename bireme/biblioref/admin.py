
from django.contrib import admin
from utils.admin import GenericAdmin

from models import *

admin.site.register(ReferenceSource)
admin.site.register(ReferenceAnalytic)
admin.site.register(ReferenceComplement)
admin.site.register(ReferenceLocal)
admin.site.register(Reference)
