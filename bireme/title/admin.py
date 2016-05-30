from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *

models = [Title, TitleVariance, BVSSpecialty, IndexRange, Audit, OnlineResources, OwnerList, IndexCode]

admin.site.register(models)
