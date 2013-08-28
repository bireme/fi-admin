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
from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.views import ACTIONS
from django.conf import settings
from datetime import datetime
from models import *
from forms import *

import mimetypes
import simplejson
import os

#from decorators import *

@login_required
def dashboard(request):

    recent_actions = LogEntry.objects.all()
    output = {}

    user = request.user
    output['recent_actions'] = recent_actions

    return render_to_response('main/index.html', output, context_instance=RequestContext(request))

############ Main table Resources #############

@login_required
def list_resources(request):

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

    resources = Resource.objects.filter(title__icontains=actions['s'])

    if not user.is_superuser:
        user_data = simplejson.loads(user.profile.data)
        user_cc = user_data['cc']
        resources = resources.filter(cooperative_center=user_cc, title__icontains=actions['s'])

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
        form = ResourceForm(request.POST, request.FILES, instance=resource, user=request.user)
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
    output['settings'] = settings

    return render_to_response('main/edit-resource.html', output, context_instance=RequestContext(request))


@login_required
def delete_resource(request, resource):

    resource = get_object_or_404(Resource, id=resource)
    output = {}

    resource.delete()
    output['alert'] = _("Resource deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))


############ Auxiliary table Thematic Area (LIS Type) #############

@login_required
def list_thematics(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

    if delete_id:
        delete_thematic(request, delete_id)

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

    thematics = ThematicArea.objects.filter(name__icontains=actions['s'])

    thematics = thematics.order_by(actions["orderby"])
    if actions['order'] == "-":
        thematics = thematic.order_by("%s%s" % (actions["order"], actions["orderby"]))


    # pagination
    pagination = {}
    paginator = Paginator(thematics, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    thematics = pagination['page'].object_list

    output['thematics'] = thematics
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('main/thematics.html', output, context_instance=RequestContext(request))

@login_required
def create_edit_thematic(request, **kwargs):

    thematic_id = kwargs.get('thematic_id')
    thematic = None
    output = {}

    if thematic_id:
        thematic = get_object_or_404(ThematicArea, id=thematic_id)
    else:
        thematic = ThematicArea(creator=request.user)
        output['is_new'] = True

    # save/update
    if request.POST:
        form = ThematicAreaForm(request.POST, request.FILES, instance=thematic)
        formset = ThematicAreaTranslationFormSet(request.POST, instance=thematic)

        if form.is_valid() and formset.is_valid():
            thematic = form.save()
            formset.save()
            output['alert'] = _("Thematic area successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('main.views.list_thematics')
    # new
    else:
        form = ThematicAreaForm(instance=thematic)
        formset = ThematicAreaTranslationFormSet(instance=thematic)

    output['form'] = form
    output['formset'] = formset
    output['thematic'] = thematic

    return render_to_response('main/edit-thematic.html', output, context_instance=RequestContext(request))


@login_required
def delete_thematic(request, thematic_id):

    thematic = get_object_or_404(ThematicArea, id=thematic_id)
    output = {}

    thematic.delete()

    output['alert'] = _("Thematic area deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/thematics.html', output, context_instance=RequestContext(request))


########## Auxiliary table Source Type ###########

@login_required
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

    types = SourceType.objects.filter(name__icontains=actions['s'])

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

    return render_to_response('main/types.html', output, context_instance=RequestContext(request))

@login_required
def create_edit_type(request, **kwargs):

    type_id = kwargs.get('type_id')
    type = None
    output = {}

    if type_id:
        type = get_object_or_404(SourceType, id=type_id)
    else:
        type = SourceType(creator=request.user)
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

            return redirect('main.views.list_types')
    # new
    else:
        form = TypeForm(instance=type)
        formset = TypeTranslationFormSet(instance=type)

    output['form'] = form
    output['formset'] = formset
    output['type'] = type

    return render_to_response('main/edit-type.html', output, context_instance=RequestContext(request))


@login_required
def delete_type(request, type):

    type = get_object_or_404(SourceType, id=type)
    output = {}

    type.delete()
    output['alert'] = _("Type deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/types.html', output, context_instance=RequestContext(request))

############ Auxiliary table Source Languages #############

@login_required
def list_languages(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')

    if delete_id:
        delete_language(request, delete_id)

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

    languages = SourceLanguage.objects.filter(name__icontains=actions['s'])

    languages = languages.order_by(actions["orderby"])
    if actions['order'] == "-":
        languages = thematic.order_by("%s%s" % (actions["order"], actions["orderby"]))


    # pagination
    pagination = {}
    paginator = Paginator(languages, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    languages = pagination['page'].object_list

    output['languages'] = languages
    output['actions'] = actions
    output['pagination'] = pagination

    return render_to_response('main/languages.html', output, context_instance=RequestContext(request))

@login_required
def create_edit_language(request, **kwargs):

    language_id = kwargs.get('language_id')
    language = None
    output = {}

    if language_id:
        language = get_object_or_404(SourceLanguage, id=language_id)
    else:
        language = SourceLanguage(creator=request.user)
        output['is_new'] = True

    # save/update
    if request.POST:
        form = LanguageForm(request.POST, request.FILES, instance=language)
        formset = LanguageTranslationFormSet(request.POST, instance=language)

        if form.is_valid() and formset.is_valid():
            language = form.save()
            formset.save()
            output['alert'] = _("Language successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('main.views.list_languages')
    # new
    else:
        form = LanguageForm(instance=language)
        formset = LanguageTranslationFormSet(instance=language)

    output['form'] = form
    output['formset'] = formset
    output['language'] = language

    return render_to_response('main/edit-language.html', output, context_instance=RequestContext(request))


@login_required
def delete_language(request, language_id):

    language = get_object_or_404(SourceLanguage, id=language_id)
    output = {}

    language.delete()

    output['alert'] = _("Language deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/languages.html', output, context_instance=RequestContext(request))
