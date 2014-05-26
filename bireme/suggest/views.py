#! coding: utf-8
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from recaptcha.client import captcha

from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.views import ACTIONS
from utils.context_processors import additional_user_info

from django.conf import settings
from datetime import datetime
from models import *
from main.models import Resource, Keyword
from events.models import Event
from forms import *

import os
import json

@csrf_exempt
def suggest_resource(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    
    suggest = SuggestResource()
   
    form = ExternalSuggestResourceForm(request.POST, instance=suggest)

    # talk to the reCAPTCHA service  
    captcha_response = captcha.submit(  
        request.POST.get('recaptcha_challenge_field'),  
        request.POST.get('recaptcha_response_field'),  
        settings.RECAPTCHA_PRIVATE_KEY,  
        request.META['REMOTE_ADDR'],)  


    if form.is_valid() and captcha_response.is_valid:
        template = 'suggest/thanks.html'
        suggest = form.save()
    else:
        template = 'suggest/invalid-link.html'
        output['form'] = form
        output['captcha_error'] = captcha_response.error_code
    
    return render_to_response(template, output, context_instance=RequestContext(request))

@login_required
def list_suggestions(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')
    suggestions = None

    if delete_id:
        delete_resource(request, delete_id)

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

    if actions['type'] and actions['type'] == 'keywords':
        suggestions = Keyword.objects.filter(user_recomendation=True, status=0, text__icontains=actions['s'])
    elif actions['type'] == 'events':
        suggestions = SuggestEvent.objects.filter(title__icontains=actions['s'])
    else:
        suggestions = SuggestResource.objects.filter(title__icontains=actions['s'])


    suggestions = suggestions.order_by(actions["orderby"])
    if actions['order'] == "-":
        suggestions = suggestions.order_by("%s%s" % (actions["order"], actions["orderby"]))

    # pagination
    pagination = {}
    paginator = Paginator(suggestions, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    suggestions = pagination['page'].object_list

    output['suggestions'] = suggestions
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('suggest/list.html', output, context_instance=RequestContext(request))

@login_required
def edit_suggested_resource(request, **kwargs):

    resource_id = kwargs.get('resource_id')
    resource = None
    form = None
    output = {}

    resource = get_object_or_404(SuggestResource, id=resource_id)

    # save/update
    if request.POST:
        form = SuggestResourceForm(request.POST, request.FILES, instance=resource)

        if form.is_valid():
            resource = form.save()

            output['alert'] = _("Resource successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('suggest.views.list_suggestions')
    # new/edit
    else:
        form = SuggestResourceForm(instance=resource)

    output['form'] = form
    output['resource'] = resource
    output['settings'] = settings

    return render_to_response('suggest/edit-suggested-resource.html', output, context_instance=RequestContext(request))


@login_required
def create_resource_from_suggestion(request, suggestion_id):

    user = request.user
    suggestion = get_object_or_404(SuggestResource, id=suggestion_id)
    output = {}

    user_data = additional_user_info(request)

    resource = Resource(title=suggestion.title, link=suggestion.link, 
        abstract=suggestion.abstract, created_by=request.user)
    resource.save();

    for tag in suggestion.keywords.split(','):
            keyword = Keyword(content_object=resource, text=tag.strip(), user_recomendation=True)
            keyword.save()

    suggestion.status = 1
    suggestion.save();

    output['alert'] = _("Resource created.")
    output['alerttype'] = "alert-success"

    return redirect('main.views.create_edit_resource', resource_id=resource.id)


@login_required
def create_event_from_suggestion(request, suggestion_id):

    user = request.user
    suggestion = get_object_or_404(SuggestEvent, id=suggestion_id)
    output = {}

    user_data = additional_user_info(request)

    event = Event(title=suggestion.title, start_date=suggestion.start_date, 
        end_date=suggestion.end_date, link=suggestion.link, city=suggestion.city, created_by=request.user)
    event.save();

    suggestion.status = 1
    suggestion.save();

    output['alert'] = _("Event created.")
    output['alerttype'] = "alert-success"

    return redirect('events.views.create_edit_event', event_id=event.id)


@csrf_exempt
def suggest_tag(request, **kwargs):

    resource = None
    response = None
    sucess = True
    
    resource_id = escape(request.POST.get('resource_id'))
    suggest_tag = escape(request.POST.get('tags'))

    try:
        resource = Resource.objects.get(pk=resource_id)
    except Resource.DoesNotExist:    
        sucess = False

    if resource != None:
        for tag in suggest_tag.split(','):
            keyword = Keyword(content_object=resource, text=tag.strip(), user_recomendation=True)
            keyword.save()


    response = HttpResponse(sucess)  
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Allow-Headers"] = "*" 
    
    return response


@csrf_exempt
def suggest_event(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    
    suggest = SuggestEvent()   
   
    form = ExternalSuggestEventForm(request.POST, instance=suggest)

    # talk to the reCAPTCHA service  
    captcha_response = captcha.submit(  
        request.POST.get('recaptcha_challenge_field'),  
        request.POST.get('recaptcha_response_field'),  
        settings.RECAPTCHA_PRIVATE_KEY,  
        request.META['REMOTE_ADDR'],)  


    if form.is_valid() and captcha_response.is_valid:
        template = 'suggest/thanks.html'
        suggest = form.save()
        output['type'] = 'event'
    else:
        template = 'suggest/invalid-link.html'
        output['form'] = form
        output['captcha_error'] = captcha_response.error_code
    
    return render_to_response(template, output, context_instance=RequestContext(request))


@login_required
def edit_suggested_event(request, **kwargs):

    suggest_id = kwargs.get('suggest_id')
    suggest = None
    form = None
    output = {}

    suggest = get_object_or_404(SuggestEvent, id=suggest_id)

    # save/update
    if request.POST:
        form = SuggestEventForm(request.POST, request.FILES, instance=suggest)

        if form.is_valid():
            suggest = form.save()

            output['alert'] = _("Event successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('suggest.views.list_suggestions')
    # new/edit
    else:
        form = SuggestEventForm(instance=suggest)

    output['form'] = form
    output['suggest'] = suggest
    output['settings'] = settings

    return render_to_response('suggest/edit-suggested-event.html', output, context_instance=RequestContext(request))

