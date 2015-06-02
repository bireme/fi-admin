from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *

models = [Title, Fascic, Mask, TitleVariance, BVSSpecialty, IndexRange, Audit, OnlineResources, OwnerList]

admin.site.register(models)
