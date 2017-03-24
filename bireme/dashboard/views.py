#! coding: utf-8
from collections import defaultdict
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext

from utils.context_processors import additional_user_info
from django.contrib.auth.decorators import login_required

from django.contrib.contenttypes.models import ContentType

from text_block.models import TextBlock
from django.contrib.admin.models import LogEntry
from django.db.models import Count, Q
from biblioref.models import Reference


@login_required
def widgets(request):
    output = {}

    current_user = request.user
    recent_actions = LogEntry.objects.filter(user=current_user)[:20]
    user_data = additional_user_info(request)
    user_roles = ['']
    user_roles.extend([role for role in user_data['service_role'].values()])

    # retrive text blocks
    text_blocks = TextBlock.objects.filter(slot='dashboard', user_profile__in=user_roles).order_by('order')

    output['recent_actions'] = recent_actions
    output['text_blocks'] = text_blocks

    return render_to_response('dashboard/index.html', output,
                              context_instance=RequestContext(request))


def last_actions(request):
    output = {}

    current_user = request.user
    recent_actions = LogEntry.objects.filter(user=current_user)[:20]
    output['recent_actions'] = recent_actions

    return render_to_response('dashboard/widget_action.html', output)


def changed_by_other_user(request):
    output = {}

    current_user = request.user
    log_list = []
    result_list = defaultdict(list)

    # get references created by current user
    refs_from_user = Reference.objects.filter(created_by=current_user)
    for reference in refs_from_user:
        # get correct class (source our analytic)
        c_type = ContentType.objects.get_for_model(reference.child_class())
        # filter by logs of current reference, change type and made by other users
        changed_by_other_user = LogEntry.objects.filter(object_id=reference.id, content_type=c_type, action_flag=2) \
                                                .exclude(user=current_user).order_by('-id')

        log_list.extend(changed_by_other_user)

    # group result (one line for each reference)
    if log_list:
        # group result by id (one line for each reference)
        for log in log_list:
            result_list[log.object_id] = log

    output['reference_list'] = result_list.values()

    return render_to_response('dashboard/widget.html', output)


def changed_by_other_cc(request):
    output = {}

    current_user = request.user
    current_user_cc = current_user.profile.get_attribute('cc')
    result_list = defaultdict(list)

    # get last references of current user cooperative center
    refs_from_cc = Reference.objects.filter(cooperative_center_code=current_user_cc).order_by('-id')[:100]

    for reference in refs_from_cc:
        # get correct class (source our analytic)
        c_type = ContentType.objects.get_for_model(reference.child_class())
        # filter by logs of current reference, change type and made by other users
        log_list = LogEntry.objects.filter(object_id=reference.id, content_type=c_type, action_flag=2) \
                                   .exclude(user=current_user).order_by('-id')

        # create list of log users of same cc
        exclude_user_list = []
        for log in log_list:
            log_user_cc = log.user.profile.get_attribute('cc')
            if log_user_cc == current_user_cc:
                exclude_user_list.append(log.user)
        # exclude from log list users from same cc as current user
        if exclude_user_list:
            log_list = log_list.exclude(user__in=exclude_user_list)

        if log_list:
            # group result by id (one line for each reference)
            for log in log_list:
                result_list[log.object_id] = log

    output['reference_list'] = result_list.values()

    return render_to_response('dashboard/widget.html', output)
