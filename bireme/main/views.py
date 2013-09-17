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

import mimetypes

import os

from decorators import *

@login_required
def dashboard(request):

    recent_actions = LogEntry.objects.all()[:20]
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

    resources = resources.order_by(actions["orderby"])
    if actions['order'] == "-":
        resources = resources.order_by("%s%s" % (actions["order"], actions["orderby"]))

    if actions['filter_owner'] != "*":
        resources = resources.filter(created_by=request.user)
    else:
        resources = resources.exclude(created_by=request.user)

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
    form = None
    formset_descriptor = None
    formset_thematic = None
    descriptor_list = None
    thematic_list = None
    output = {}

    if resource_id:
        resource = get_object_or_404(Resource, id=resource_id)
    else:
        resource = Resource(created_by=request.user)
        output['is_new'] = True

    user_data = additional_user_info(request)
    user_data['is_owner'] = True if resource.created_by_id == request.user.id else False

    # save/update
    if request.POST:
        form = ResourceForm(request.POST, request.FILES, instance=resource, user=request.user, user_data=user_data)
        formset_descriptor = DescriptorFormSet(request.POST, instance=resource)
        formset_thematic = ResourceThematicFormSet(request.POST, instance=resource)

        if form.is_valid() and formset_descriptor.is_valid() and formset_thematic.is_valid():
            resource = form.save()
            form.save_m2m()

            # if documentalist process descriptors
            '''
            if user_data['user_role'] == 'doc':
                for fd in formset_descriptor:
                    print "tenta salvar descritor"
                    descriptor_obj = fd.save(commit=False)
                    # set status to pending and save user
                    descriptor_obj.status = 0
                    descriptor_obj.creator = request.user
                    descriptor_obj.resource_id = resource.id
                    descriptor_obj.save()

                for ft in formset_thematic:
                    print "tenta salvar tema"
                    thematic_obj = ft.save(commit=False)
                    # set status to pending and save user
                    thematic_obj.status = 0
                    thematic_obj.creator = request.user
                    thematic_obj.resource_id = resource.id
                    thematic_obj.save()
            '''

            formset_descriptor.save()
            formset_thematic.save()

            output['alert'] = _("Resource successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('main.views.list_resources')
    # new/edit
    else:
        form = ResourceForm(instance=resource, user_data=user_data)

        # if documentalist create a formset with descriptors created by the user
        if user_data['user_role'] == 'doc':
            descriptor_list = Descriptor.objects.filter(resource=resource).exclude(created_by_id=request.user.id)
            thematic_list = ResourceThematic.objects.filter(resource=resource).exclude(created_by_id=request.user.id)

            pending_descriptor_from_user = Descriptor.objects.filter(created_by_id=request.user.id, status=0)
            pending_thematic_from_user = ResourceThematic.objects.filter(created_by_id=request.user.id, status=0)

            formset_descriptor = DescriptorFormSet(instance=resource, queryset=pending_descriptor_from_user)
            formset_thematic = ResourceThematicFormSet(instance=resource, queryset=pending_thematic_from_user)
        else:
            formset_descriptor = DescriptorFormSet(instance=resource)
            formset_thematic = ResourceThematicFormSet(instance=resource)

    output['form'] = form
    output['formset_descriptor'] = formset_descriptor
    output['formset_thematic'] = formset_thematic
    output['resource'] = resource
    output['descriptor_list'] = descriptor_list
    output['thematic_list'] = thematic_list
    output['settings'] = settings
    output['user_data'] = user_data

    return render_to_response('main/edit-resource.html', output, context_instance=RequestContext(request))


@login_required
def delete_resource(request, resource):

    resource = get_object_or_404(Resource, id=resource)
    output = {}

    user_data = additional_user_info(request)

    if user_data['user_role'] == 'doc' and resource.created_by_id != user.id:
        return HttpResponse('Unauthorized', status=401)

    resource.delete()

    output['alert'] = _("Resource deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))


############ Auxiliary table Thematic Area (LIS Type) #############

@login_required
@superuser_permission
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
@superuser_permission
def create_edit_thematic(request, **kwargs):

    thematic_id = kwargs.get('thematic_id')
    thematic = None
    output = {}

    if thematic_id:
        thematic = get_object_or_404(ThematicArea, id=thematic_id)
    else:
        thematic = ThematicArea(created_by=request.user)
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
@superuser_permission
def delete_thematic(request, thematic_id):

    thematic = get_object_or_404(ThematicArea, id=thematic_id)
    output = {}

    thematic.delete()

    output['alert'] = _("Thematic area deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/thematics.html', output, context_instance=RequestContext(request))


########## Auxiliary table Source Type ###########

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
@superuser_permission
def create_edit_type(request, **kwargs):

    type_id = kwargs.get('type_id')
    type = None
    output = {}

    if type_id:
        type = get_object_or_404(SourceType, id=type_id)
    else:
        type = SourceType(created_by=request.user)
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
@superuser_permission
def delete_type(request, type):

    type = get_object_or_404(SourceType, id=type)
    output = {}

    type.delete()
    output['alert'] = _("Type deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/types.html', output, context_instance=RequestContext(request))

############ Auxiliary table Source Languages #############

@login_required
@superuser_permission
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
@superuser_permission
def create_edit_language(request, **kwargs):

    language_id = kwargs.get('language_id')
    language = None
    output = {}

    if language_id:
        language = get_object_or_404(SourceLanguage, id=language_id)
    else:
        language = SourceLanguage(created_by=request.user)
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
@superuser_permission
def delete_language(request, language_id):

    language = get_object_or_404(SourceLanguage, id=language_id)
    output = {}

    language.delete()

    output['alert'] = _("Language deleted.")
    output['alerttype'] = "alert-success"

    return render_to_response('main/languages.html', output, context_instance=RequestContext(request))
