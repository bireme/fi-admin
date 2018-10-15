# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _, get_language
from django.db import models
from django.utils import timezone
from utils.models import Generic, Country
from django.contrib.contenttypes.generic import GenericRelation
from main.models import SourceLanguage


from .models_thesaurus import *
from .models_qualifiers import *
from .models_descriptors import *
