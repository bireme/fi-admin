#! coding: utf-8
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage

from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.views import logout

from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry
from django.db.models import Q

from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.views import ACTIONS
from utils.context_processors import additional_user_info
from utils.forms import is_valid_for_publication
from django.conf import settings
from datetime import datetime
from models import *
from suggest.models import *
from help.models import get_help_fields
from forms import *
from error_reporting.forms import ErrorReportForm

import mimetypes

import os

from decorators import *

############ Resources (LIS) #############

@login_required
def list_resources(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')
    # save current url for preserve filters after edit
    request.session["filtered_list"] = request.get_full_path()

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

    # check if user has perform a search
    search = actions['s']
    if search:
        # search by id
        if search.isdigit():
            resources = Resource.objects.filter(pk=int(search))
        # search by field
        elif ":" in search:
            search_parts = actions["s"].split(":")
            search_field = search_parts[0] + "__icontains"
            search = search_parts[1]
            resources = Resource.objects.filter(**{search_field: search})
        # free search
        else:
            search_method = 'search' if settings.FULLTEXT_SEARCH else 'icontains'
            search_field1 = 'title__' + search_method
            search_field2 = 'link__' + search_method

            if settings.FULLTEXT_SEARCH:
                # search using boolean AND
                search = u"+{}".format(search.replace(' ', ' +'))

            resources = Resource.objects.filter( Q(**{search_field1: search}) | Q(**{search_field2: search}))
    else:
        resources = Resource.objects.all()


    if actions['filter_status'] != '':
        resources = resources.filter(status=actions['filter_status'])

    if actions['filter_thematic'] != '':
        actions['filter_thematic'] = int(actions['filter_thematic'])
        resources = resources.filter(thematics__thematic_area=actions['filter_thematic'])


    resources = resources.order_by(actions["orderby"])
    if actions['order'] == "-":
        resources = resources.order_by("%s%s" % (actions["order"], actions["orderby"]))

    user_data = additional_user_info(request)

    if actions['filter_owner'] == "network":
        resources = resources.filter(cooperative_center_code__in=user_data['ccs'])
    elif actions['filter_owner'] != "*":
        resources = resources.filter(created_by=request.user)
    else:
        resources = resources.all()

    # populate thematic list for filter
    thematic_list = ThematicArea.objects.all().order_by('name')

    # pagination
    pagination = {}
    paginator = Paginator(resources, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    try:
        pagination['page'] = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages if int(page) > 1 else 1
        pagination['page'] = paginator.page(page)

    resources = pagination['page'].object_list

    output['resources'] = resources
    output['thematic_list'] = thematic_list
    output['actions'] = actions
    output['pagination'] = pagination
    output['user_data'] = user_data

    return render_to_response('main/resources.html', output, context_instance=RequestContext(request))

@login_required
def create_edit_resource(request, **kwargs):

    resource_id = kwargs.get('resource_id')
    resource = None
    form = None
    form_error_report = None
    formset_descriptor = None
    formset_thematic = None
    formset_keyword  = None
    descriptor_list  = None
    keyword_list     = None
    thematic_list    = None
    valid_for_publication = True
    output = {}

    if resource_id:
        resource = get_object_or_404(Resource, id=resource_id)
    else:
        resource = Resource(created_by=request.user)
        output['is_new'] = True

    user_data = additional_user_info(request)
    user_data['is_owner'] = True if resource.created_by_id == request.user.id else False
    user_role = user_data['service_role'].get('LIS')

    ct = ContentType.objects.get_for_model(resource)

    # save/update
    if request.POST:
        form = ResourceForm(request.POST, request.FILES, instance=resource, user=request.user, user_data=user_data)
        formset_descriptor = DescriptorFormSet(request.POST, instance=resource)
        formset_keyword    = KeywordFormSet(request.POST, instance=resource)
        formset_thematic   = ResourceThematicFormSet(request.POST, instance=resource)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_keyword_valid  = formset_keyword.is_valid()
        formset_thematic_valid = formset_thematic.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(form,
            [formset_descriptor, formset_keyword, formset_thematic])

        if (form_valid and formset_descriptor_valid and formset_keyword_valid
                and formset_thematic_valid and valid_for_publication):

            if not resource.id:
                resource = form.save()

            formset_descriptor.save()
            formset_keyword.save()
            formset_thematic.save()

            # update solr index
            form.save()
            form.save_m2m()

            output['alert'] = _("Resource successfully edited.")
            output['alerttype'] = "alert-success"

            redirect_url = request.session.get("filtered_list", 'main.views.list_resources')

            return redirect(redirect_url)
    # new/edit
    else:
        form = ResourceForm(instance=resource, user_data=user_data)

        form_error_report = ErrorReportForm()

        # if documentalist create a formset with descriptors created by the user
        if user_role == 'doc':
            descriptor_list = Descriptor.objects.filter(object_id=resource.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)
            keyword_list = Keyword.objects.filter(object_id=resource.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)
            thematic_list = ResourceThematic.objects.filter(object_id=resource.id, content_type=ct).exclude(created_by_id=request.user.id, status=0)

            pending_descriptor_from_user = Descriptor.objects.filter(created_by_id=request.user.id, status=0)
            pending_keyword_from_user = Keyword.objects.filter(created_by_id=request.user.id, status=0)
            pending_thematic_from_user = ResourceThematic.objects.filter(created_by_id=request.user.id, status=0)

            formset_descriptor = DescriptorFormSet(instance=resource, queryset=pending_descriptor_from_user)
            formset_keyword  = KeywordFormSet(instance=resource, queryset=pending_keyword_from_user)
            formset_thematic = ResourceThematicFormSet(instance=resource, queryset=pending_thematic_from_user)
        else:
            formset_descriptor = DescriptorFormSet(instance=resource)
            formset_keyword  = KeywordFormSet(instance=resource)
            formset_thematic = ResourceThematicFormSet(instance=resource)

    output['form'] = form
    output['formset_descriptor'] = formset_descriptor
    output['formset_keyword']  = formset_keyword
    output['formset_thematic'] = formset_thematic
    output['form_error_report'] = form_error_report
    output['valid_for_publication'] = valid_for_publication

    output['content_type'] = ct.id

    output['resource'] = resource
    output['descriptor_list'] = descriptor_list
    output['keyword_list'] = keyword_list
    output['thematic_list'] = thematic_list
    output['settings'] = settings
    output['user_data'] = user_data
    output['user_role'] = user_role
    output['help_fields'] = get_help_fields('resources')

    return render_to_response('main/edit-resource.html', output, context_instance=RequestContext(request))


@login_required
def delete_resource(request, resource_id):

    user = request.user
    resource = get_object_or_404(Resource, id=resource_id)
    c_type = ContentType.objects.get_for_model(Resource)
    output = {}

    user_data = additional_user_info(request)

    if resource.created_by_id != user.id:
        return HttpResponse('Unauthorized', status=401)

    resource.delete()

    # delete associated data
    Descriptor.objects.filter(object_id=resource_id, content_type=c_type).delete()
    Keyword.objects.filter(object_id=resource_id, content_type=c_type).delete()
    ResourceThematic.objects.filter(object_id=resource_id, content_type=c_type).delete()

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
        thematics = thematics.order_by("%s%s" % (actions["order"], actions["orderby"]))


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
        languages = languages.order_by("%s%s" % (actions["order"], actions["orderby"]))


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
