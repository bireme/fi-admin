#! coding: utf-8
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.views import logout

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry

from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.views import ACTIONS
from utils.context_processors import additional_user_info
from django.conf import settings
from datetime import datetime
from models import *
from forms import *

from main.decorators import *

import mimetypes

import os

@login_required
def list_events(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

    if delete_id:
        delete_event(request, delete_id)

    # getting action parameters
    actions = {}
    for key in ACTIONS.keys():
        if request.REQUEST.get(key):
            actions[key] = request.REQUEST.get(key)
        else:
            actions[key] = ACTIONS[key]

    page = 1
    if actions['page'] and actions['page'] != '':
        page = actions['page']

    events = Event.objects.filter(title__icontains=actions['s'])

    events = events.order_by(actions["orderby"])
    if actions['order'] == "-":
        events = events.order_by("%s%s" % (actions["order"], actions["orderby"]))

    if actions['filter_owner'] != "*":
        events = events.filter(created_by=request.user)
    else:
        events = events.exclude(created_by=request.user)

    # pagination
    pagination = {}
    paginator = Paginator(events, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    events = pagination['page'].object_list

    output['events'] = events
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('events/events.html', output, context_instance=RequestContext(request))


@login_required
def create_edit_event(request, **kwargs):

    event_id = kwargs.get('event_id')
    event = None
    form = None
    formset_descriptor = None
    formset_thematic = None
    formset_keyword  = None
    descriptor_list  = None
    keyword_list     = None
    thematic_list    = None
    output = {}

    if event_id:
        event = get_object_or_404(Event, id=event_id)
    else:
        event = Event(created_by=request.user)
        output['is_new'] = True

    user_data = additional_user_info(request)
    user_data['is_owner'] = True if event.created_by_id == request.user.id else False

    ct = ContentType.objects.get_for_model(event)

    # save/update
    if request.POST:
        form = EventForm(request.POST, request.FILES, instance=event, user=request.user, user_data=user_data)
        formset_descriptor = DescriptorFormSet(request.POST, instance=event)
        formset_keyword    = KeywordFormSet(request.POST, instance=event)
        formset_thematic   = ResourceThematicFormSet(request.POST, instance=event)

        if form.is_valid() and formset_descriptor.is_valid() and formset_keyword.is_valid() and formset_thematic.is_valid():
            event = form.save()
            form.save_m2m()

            formset_descriptor.save()
            formset_keyword.save()
            formset_thematic.save()

            output['alert'] = _("Event successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('events.views.list_events')
    # new/edit
    else:
        form = EventForm(instance=event, user_data=user_data)

        # if documentalist create a formset with descriptors created by the user
        if user_data['user_role'] == 'doc':
            descriptor_list = Descriptor.objects.filter(object_id=event.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)
            keyword_list = Keyword.objects.filter(object_id=event.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)
            thematic_list = ResourceThematic.objects.filter(object_id=event.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)

            pending_descriptor_from_user = Descriptor.objects.filter(created_by_id=request.user.id, status=0)
            pending_keyword_from_user = Keyword.objects.filter(created_by_id=request.user.id, status=0)
            pending_thematic_from_user = ResourceThematic.objects.filter(created_by_id=request.user.id, status=0)

            formset_descriptor = DescriptorFormSet(instance=event, queryset=pending_descriptor_from_user)
            formset_keyword  = KeywordFormSet(instance=event, queryset=pending_keyword_from_user)
            formset_thematic = ResourceThematicFormSet(instance=event, queryset=pending_thematic_from_user)
        else:
            formset_descriptor = DescriptorFormSet(instance=event)
            formset_keyword  = KeywordFormSet(instance=event)            
            formset_thematic = ResourceThematicFormSet(instance=event)

    output['form'] = form
    output['formset_descriptor'] = formset_descriptor
    output['formset_keyword']  = formset_keyword
    output['formset_thematic'] = formset_thematic
    output['event'] = event
    output['descriptor_list'] = descriptor_list
    output['keyword_list'] = keyword_list
    output['thematic_list'] = thematic_list
    output['settings'] = settings
    output['user_data'] = user_data

    return render_to_response('events/edit-event.html', output, context_instance=RequestContext(request))


@login_required
def delete_event(request, event_id):

    user = request.user
    event = get_object_or_404(Event, id=event_id)
    output = {}

    user_data = additional_user_info(request)

    if resource.created_by_id != user.id:
        return HttpResponse('Unauthorized', status=401)

    resource.delete()

    output['alert'] = _("Event deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('events/events.html', output, context_instance=RequestContext(request))


########## Auxiliary table event type ###########

@login_required
@superuser_permission
def list_types(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

    if delete_id:
        delete_type(request, delete_id)

    # getting action parameters
    actions = {}
    for key in ACTIONS.keys():
        if request.REQUEST.get(key):
            actions[key] = request.REQUEST.get(key)
        else:
            actions[key] = ACTIONS[key]

    page = 1
    if actions['page'] and actions['page'] != '':
        page = actions['page']

    types = EventType.objects.filter(name__icontains=actions['s'])

    types = types.order_by(actions["orderby"])
    if actions['order'] == "-":
        types = types.order_by("%s%s" % (actions["order"], actions["orderby"]))


    # pagination
    pagination = {}
    paginator = Paginator(types, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    types = pagination['page'].object_list

    output['types'] = types
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('events/types.html', output, context_instance=RequestContext(request))

@login_required
@superuser_permission
def create_edit_type(request, **kwargs):

    type_id = kwargs.get('type_id')
    type = None
    output = {}

    if type_id:
        type = get_object_or_404(EventType, id=type_id)
    else:
        type = EventType(created_by=request.user)
        output['is_new'] = True

    # save/update
    if request.POST:
        form = TypeForm(request.POST, request.FILES, instance=type)
        formset = TypeTranslationFormSet(request.POST, instance=type)

        if form.is_valid() and formset.is_valid():
            type = form.save()
            formset.save()
            output['alert'] = _("Type successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('events.views.list_types')
    # new
    else:
        form = TypeForm(instance=type)
        formset = TypeTranslationFormSet(instance=type)

    output['form'] = form
    output['formset'] = formset
    output['type'] = type

    return render_to_response('events/edit-type.html', output, context_instance=RequestContext(request))


@login_required
@superuser_permission
def delete_type(request, type):

    type = get_object_or_404(EventType, id=type)
    output = {}

    type.delete()
    output['alert'] = _("Type deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('events/types.html', output, context_instance=RequestContext(request))
