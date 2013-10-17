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

from django.conf import settings
from datetime import datetime
from models import *
from main.models import Resource, Keyword
from forms import *

import os
import json

@csrf_exempt
def suggest_resource(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    
    suggest = SuggestResource()
   
    form = SuggestResourceForm(request.POST, instance=suggest)

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
        print form.errors
    
    return render_to_response(template, output, context_instance=RequestContext(request))

@login_required
def list_suggested_resources(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

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

    resources = SuggestResource.objects.filter(title__icontains=actions['s'])

    resources = resources.order_by(actions["orderby"])
    if actions['order'] == "-":
        resources = resources.order_by("%s%s" % (actions["order"], actions["orderby"]))

    # pagination
    pagination = {}
    paginator = Paginator(resources, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    resources = pagination['page'].object_list

    output['resources'] = resources
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('suggest/resources.html', output, context_instance=RequestContext(request))

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

            return redirect('suggest.views.list_suggested_resources')
    # new/edit
    else:
        form = SuggestResourceForm(instance=resource)

    output['form'] = form
    output['resource'] = resource
    output['settings'] = settings

    return render_to_response('suggest/edit-suggested-resource.html', output, context_instance=RequestContext(request))


@login_required
def delete_resource(request, resource):

    user = request.user
    resource = get_object_or_404(Resource, id=resource)
    output = {}

    user_data = additional_user_info(request)

    if resource.created_by_id != user.id:
        return HttpResponse('Unauthorized', status=401)

    resource.delete()

    output['alert'] = _("Resource deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))



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
            keyword = Keyword(resource=resource, text=tag.strip(), user_recomendation=True)
            keyword.save()


    response = HttpResponse(sucess)  
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Allow-Headers"] = "*" 
    
    return response
