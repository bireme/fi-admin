#! coding: utf-8
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.views import logout

from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.views import ACTIONS
from django.conf import settings
from datetime import datetime
from models import *
from forms import *

import mimetypes
import os

#from decorators import *

@login_required
def dashboard(request):
    
    user = request.user
    output = {}

    return render_to_response('main/index.html', output, context_instance=RequestContext(request))

@login_required
def list_resources(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

    print request.POST

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

    resources = Resource.objects.filter(title__icontains=actions['s'])

    if not user.is_superuser:
        resources = resources.filter(responsible=user.profile.cooperative_center)

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

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))

@login_required
def create_edit_resource(request, **kwargs):

    resource_id = kwargs.get('resource_id')
    resource = None
    output = {}

    if resource_id:
        resource = get_object_or_404(Resource, id=resource_id)
    else:
        resource = Resource(creator=request.user)
        output['is_new'] = True

    # save/update
    if request.POST:
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        formset = DescriptorFormSet(request.POST, instance=resource)
        
        if form.is_valid() and formset.is_valid():
            resource = form.save()
            formset.save()
            output['alert'] = _("Resource successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('main.views.list_resources')
    # new            
    else:
        form = ResourceForm(instance=resource)
        formset = DescriptorFormSet(instance=resource)
        
    output['form'] = form
    output['formset'] = formset
    output['resource'] = resource
    
    return render_to_response('main/edit-resource.html', output, context_instance=RequestContext(request))


@login_required
def delete_resource(request, resource):

    resource = get_object_or_404(Resource, id=resource)
    output = {}

    resource.delete()
    output['alert'] = _("Resource deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))
