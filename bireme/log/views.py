#! coding: utf-8
from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from django.views.generic.edit import UpdateView
from utils.views import LoginRequiredView
from django.template import RequestContext

from log.models import LogReview
from log.forms import LogReviewForm

def view_log(request, ctype_id, obj_id):
    """
    List all changes of a object
    """
    logs = LogEntry.objects.filter(content_type_id=ctype_id, object_id=obj_id)

    return render(request, 'log/list.html', {'logs': logs})


def review_log(request, type, ctype_id, obj_id):
    """
    Display list of record changes and allow user to select status (approved/not approved)
    """
    current_user = request.user

    log_list = LogEntry.objects.filter(content_type_id=ctype_id, object_id=obj_id)


    if type == 'user':
        # exclude changes made by the current user
        log_list = log_list.exclude(user=current_user)
    elif type == 'cc':
        current_user_cc = current_user.profile.get_attribute('cc')
        # exclude from log list users from same cc as current user
        exclude_user_list = []
        for log in log_list:
            log_user_cc = log.user.profile.get_attribute('cc')
            if log_user_cc == current_user_cc:
                exclude_user_list.append(log.user)

        if exclude_user_list:
            log_list = log_list.exclude(user__in=exclude_user_list)

    if log_list:
        reference_type = log_list[0].content_type.model
        reference_id = log_list[0].object_id

    return render(request, 'log/review.html', {'logs': log_list,
                                                  'reference_type': reference_type,
                                                  'reference_id': reference_id})


def update_review(request):
    """
    Create log review objects with status (approved/not approved) of each record change
    """

    not_approved_list = []
    # iterate for all params in the form
    for param, value in request.POST.iteritems():
        # check for review params (review_ID-OF-LOGENTRY)
        if 'review_' in param and value != '':
            # extract logentry id from param name
            log_id = param.split('_')[1]
            # get or create a new object at logreview table
            log_review, created = LogReview.objects.get_or_create(log_id=log_id)
            log_review.log_id = log_id
            log_review.status = value
            log_review.save()

            if value == '-1':
                # create list of no approved changes for user manually fix on record
                not_approved_list.append(log_id)

    # if user has not approved one or more changes present list for final revision
    if not_approved_list:
        # get log entry objects for display
        not_approved_logs = LogEntry.objects.filter(id__in=not_approved_list)
        # get content type and ID of first logentry to redirect user to edit source or analytic page
        reference_type = not_approved_logs[0].content_type.model
        reference_id = not_approved_logs[0].object_id

        return render('log/review_notapproved.html',
                    {'logs': not_approved_logs, 'reference_type': reference_type,
                    'reference_id': reference_id})

    else:
        return redirect('dashboard')
