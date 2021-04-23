#! coding: utf-8
import os
import json
import requests
import math
import re

from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from django.conf import settings
from datetime import datetime
from main.models import Resource, Keyword

from urllib import unquote

@csrf_exempt
def search(request):

    output = {}

    # set encoding of old LIS interface to avoid problems with words with accent
    request.encoding = 'iso-8859-1'

    params = request.POST if request.method == 'POST' else request.GET

    # LIS old interface send newexpr, expr or key (topics) to inform query
    q = params.get('newexpr', '')
    q = params.get('expr', q)
    tl = params.get('TL', '')

    key = params.get('key', '')
    # handle search by topic
    if key:
        # topic search format: ((descriptor/(323)) AND TL=LISBRXX
        key_search = re.search( r'AND TL=(.*)', key)
        if key_search:
            tl = key_search.group(1)

        # remove old search by field 323 (descriptor)
        q = re.sub(r'\/\(323\)', '', key)
        # remove TL from expression
        q = re.sub(r'AND TL=.*$', '', q)

    page = params.get('page', '1')
    op = params.get('op', 'search')
    sort = params.get('sort', 'created_date desc')
    count = '10'

    start = ((int(page) * int(count)) - int(count)) + 1

    # check if user is searching for all resources ($)
    if q == '$':
        q = ''

    # filter result by approved resources (status=1)
    if tl != '':
        fq = '(status:1 AND django_ct:main.resource) AND thematic_area:"%s"' % tl
    else:
        fq = '(status:1 AND django_ct:main.resource)'

    # url
    search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

    search_params = {'site': settings.SEARCH_INDEX, 'op': op,'output': 'site', 'lang': 'pt',
                'q': q , 'fq': fq,  'start': start, 'count': count, 'id' : id,'sort': sort}

    request_result = requests.post(search_url, data=search_params)
    result = request_result.json()
    total = result['diaServerResponse'][0]['response']['numFound']

    pages_count = 10
    total_pages = math.ceil( total / float(pages_count) )
    page_navigation_end = math.ceil( int(page) / float(pages_count) ) * pages_count
    page_navigation_start = (page_navigation_end - pages_count) + 1

    if page_navigation_end > total_pages:
        page_navigation_end = total_pages

    page_navigation = range( int(page_navigation_start), int(page_navigation_end)+1)

    output['from'] = start
    output['to'] = (int(start) + int(count)) -1
    output['page'] = int(page)
    output['expr'] = q
    output['total'] = total
    output['result'] = result
    output['page_navigation'] = page_navigation
    output['page_navigation_start'] = int(page_navigation_start)
    output['page_navigation_end'] = int(page_navigation_end)
    output['page_navigation_prev_block'] = int(page_navigation_start - pages_count)
    output['page_navigation_next_block'] = int(page_navigation_start + pages_count)
    output['page_navigation_last_page'] = int(total_pages)

    # render the template and convert the result to ISO-8859-1
    render_xml = render_to_string('api/lis_old_search.xml', output)
    result_iso = render_xml.encode('iso-8859-1')

    return HttpResponse(result_iso, mimetype="text/xml; charset=iso-8859-1")
