#! coding: utf-8
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.context_processors import additional_user_info

from django.conf import settings
from datetime import datetime

from main.models import Resource, Keyword
from events.models import Event
from error_reporting.models import *
from error_reporting.forms import *

import os
import json

@login_required
def list_error_report(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')
    error_reports = None

    if delete_id:
        delete_error_report(request, delete_id)

    # getting action parameters
    actions = {}
    for key in settings.ACTIONS.keys():
        if request.GET.get(key):
            actions[key] = request.GET.get(key)
        else:
            actions[key] = settings.ACTIONS[key]

    page = 1
    if actions['page'] and actions['page'] != '':
        page = actions['page']

    ct = ContentType.objects.get_for_model(Resource)

    if actions['type'] and actions['type'] == 'events':
        ct = ContentType.objects.get_for_model(Event)
        error_reports = ErrorReport.objects.filter(content_type=ct, object_id__icontains=actions['s'])
    else:
        ct = ContentType.objects.get_for_model(Resource)
        error_reports = ErrorReport.objects.filter(content_type=ct, object_id__icontains=actions['s'])

    error_reports = error_reports.order_by(actions["orderby"])
    if actions['order'] == "-":
        error_reports = error_reports.order_by("%s%s" % (actions["order"], actions["orderby"]))

    # pagination
    pagination = {}
    paginator = Paginator(error_reports, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    error_reports = pagination['page'].object_list

    output['error_reports'] = error_reports
    output['actions'] = actions
    output['pagination'] = pagination

    return render(request, 'error_report/list.html', output)


@login_required
def create_error_report(request, **kwargs):

    error_report = None
    form = None

    object_id = escape(request.POST.get('object_id'))
    content_type = escape(request.POST.get('content_type'))
    return_url = request.POST.get('return_url')

    error_report = ErrorReport(object_id=object_id, content_type_id=content_type)
    form = ErrorReportForm(request.POST, instance=error_report)
    error_report = form.save()

    return redirect(return_url, resource_id=object_id)


@login_required
def edit_error_report(request, **kwargs):

    report_id = kwargs.get('report_id')
    error_report = None
    form = None
    output = {}

    if report_id:
        error_report = get_object_or_404(ErrorReport, id=report_id)
    else:
        error_report = ErrorReport(created_by=request.user)
        output['is_new'] = True

    # save/update
    if request.POST:
        form = ErrorReportForm(request.POST, request.FILES, instance=error_report)

        if form.is_valid():
            error_report = form.save()

            output['alert'] = _("Report successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('error_reporting:list_error_report')
    # new/edit
    else:
        form = ErrorReportForm(instance=error_report)

    output['form'] = form
    output['error_report'] = error_report
    output['settings'] = settings

    return render(request, 'error_report/edit.html', output)


@csrf_exempt
def external_error_report(request, **kwargs):

    error_report = None
    response = None
    sucess = True

    resource_id = escape(request.POST.get('resource_id'))
    resource_type = escape(request.POST.get('resource_type', 'resource'))

    content_type = ContentType.objects.get(model=resource_type)

    error_report = ErrorReport(object_id=resource_id, content_type=content_type, status=0)
    form = ExternalErrorReportForm(request.POST, instance=error_report)

    if form.is_valid():
        sucess = True
        error_report = form.save()
    else:
        sucess = False

    response = HttpResponse(sucess)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Allow-Headers"] = "*"

    return response


@login_required
def delete_error_report(request, error_report_id):

    user = request.user
    error_report = get_object_or_404(ErrorReport, id=error_report_id)
    output = {}

    user_data = additional_user_info(request)

    if error_report.created_by_id != user.id:
        return HttpResponse('Unauthorized', status=401)

    error_report.delete()

    output['alert'] = _("Report deleted.")
    output['alerttype'] = "alert-success"

    return render(request, 'error_reporting/list.html', output)
