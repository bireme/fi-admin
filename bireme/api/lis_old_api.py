#! coding: utf-8
import os
import json
import requests
import math

from django.shortcuts import redirect, render_to_response, get_object_or_404
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


def search(request):

    output = {}

    q = request.GET.get('expr', '')
    tl = request.GET.get('TL', '')
    page = request.GET.get('page', '1')
    op = request.GET.get('op', 'search')
    sort = request.GET.get('sort', 'created_date desc')
    count = '10'

    start = ((int(page) * int(count)) - int(count)) + 1

    # filter result by approved resources (status=1)
    if tl != '':
        fq = '(status:1 AND django_ct:main.resource) AND thematic_area:%s' % tl
    else:
        fq = '(status:1 AND django_ct:main.resource)'

    # url
    search_url = "%siahx-controller/" % settings.SEARCH_SERVICE_URL

    search_params = {'site': 'fi', 'col': 'main','op': op,'output': 'site', 'lang': 'pt', 
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
