# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

field_tag_map = {'cc_code': '607', 'name': '611', 'acronym': '611',
                 'address': '615', 'mailbox': '616', 'zipcode': '616',
                 'city': '617', 'state': '618', 'country': '620'
                }
