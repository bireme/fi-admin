# coding: utf-8
from django.utils.translation import ugettext_lazy as _

import colander
import deform
import json

field_tag_map = {'cc_code': '607', 'name': '611', 'category': '603', 'type': '604',
                 'address': '615', 'mailbox': '616', 'zipcode': '616', 'contact_person': '610',
                 'contact_person': '610', 'contact_email': '624', 'contact_phone': '621',
                 'city': '617', 'state': '618', 'country': '620', 'country_area_code': '625',
                 'url':  '694', 'id': '99', 'unit_1': '612', 'unit_2': '613', 'unit_3': '614'
                }
