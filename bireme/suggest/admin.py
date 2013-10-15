from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import *
from utils.admin import GenericAdmin



admin.site.register(SuggestResource)
