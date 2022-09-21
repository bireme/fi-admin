#! coding: utf-8
from collections import defaultdict

import requests
from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.shortcuts import redirect, render, get_object_or_404
from django.template import RequestContext
from requests.exceptions import ConnectionError, HTTPError, SSLError, Timeout
from text_block.models import TextBlock

from biblioref.models import Reference
from biblioref.views import refs_changed_by_other_cc, refs_changed_by_other_user, refs_llxp_for_indexing
from institution.models import Institution
from utils.context_processors import additional_user_info


@login_required
def widgets(request):
    output = {}

    current_user = request.user
    user_data = additional_user_info(request)
    user_roles = ['']
    user_roles.extend([role for role in user_data['service_role'].values()])
    institution_id = ''

    # retrive text blocks
    text_blocks = TextBlock.objects.filter(slot='dashboard', user_profile__in=user_roles, display=True).order_by('order')

    if 'DirIns' in user_data['service_role']:
        try:
            institution_id = Institution.objects.get(cc_code=user_data['user_cc']).id
        except Institution.DoesNotExist:
            institution_id = None

    try:
        dedup_response = requests.get(settings.DEDUP_SERVICE_URL)
        output['dedup_is_unavailable'] = (dedup_response.status_code >= 400)
    except (ConnectionError, HTTPError, SSLError, Timeout):
        output['dedup_is_unavailable'] = True

    output['institution_id'] = institution_id
    output['text_blocks'] = text_blocks

    return render(request, 'dashboard/index.html', output)



def last_actions(request):
    output = {}

    current_user = request.user
    recent_actions = LogEntry.objects.filter(user=current_user)
    output['recent_actions'] = recent_actions[:10]

    return render(request, 'dashboard/widget_action.html', output)


def changed_by_others(request, review_type):
    output = {}
    ref_list = []

    if review_type == 'user':
        ref_list = refs_changed_by_other_user(request.user)
    elif review_type == 'cc':
        ref_list = refs_changed_by_other_cc(request.user)

    if ref_list:
        ref_list = ref_list.values()

    output['reference_list'] = ref_list
    output['review_type'] = review_type

    return render(request, 'dashboard/widget_log_review.html', output)


def llxp_indexed_by_cc(request):
    output = {}
    ref_list = []

    ref_list = refs_llxp_for_indexing(request.user)

    output['reference_list'] = ref_list[:10]

    return render(request, 'dashboard/widget_edit_reference.html', output)
