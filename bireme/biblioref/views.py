#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from deform.exception import ValidationFailure

from field_definitions import FIELDS_BY_DOCUMENT_TYPE

from utils.views import ACTIONS
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info
from attachments.models import Attachment
from main.models import Descriptor
from title.models import Title
from help.models import get_help_fields
from utils.views import LoginRequiredView
from urlparse import parse_qsl
from pkg_resources import resource_filename
from forms import *

import colander
import deform
import json


class BiblioRefGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for bibliographic references objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    context_object_name = "references"
    search_field = "reference_title"

    def dispatch(self, *args, **kwargs):
        return super(BiblioRefGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        source_id = self.request.GET.get('source', None)
        document_type = self.request.GET.get('document_type', None)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        search_field = self.search_field + '__contains'

        object_list = self.model.objects.filter(**{search_field: self.actions['s']})

        if source_id:
            object_list = object_list.filter(source_id=source_id)

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        # filter by specific document type and remove filter by user (filter_owner)
        if document_type:
            object_list = object_list.filter(literature_type=document_type)

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # if is list of a specific source or source type dont't filter by user
        if source_id or document_type:
            self.actions['filter_owner'] = '*'

        # profile lilacs express editor - restrict by CC code when list sources
        if document_type and user_role == 'editor_llxp':
            self.actions['filter_owner'] = 'center'

        # filter by user
        if not self.actions['filter_owner'] or self.actions['filter_owner'] == 'user':
            object_list = object_list.filter(created_by=self.request.user)
        # filter by cooperative center
        elif self.actions['filter_owner'] == 'center':
            user_cc = self.request.user.profile.get_attribute('cc')
            object_list = object_list.filter(cooperative_center_code=user_cc)
        # filter by titles of responsibility of current user CC
        elif self.actions['filter_owner'] == 'indexed':
            user_cc = self.request.user.profile.get_attribute('cc')
            titles_indexed = [t.shortened_title for t in Title.objects.filter(indexer_cc_code=user_cc)]
            filter_title_qs = Q()
            for title in titles_indexed:
                filter_title_qs = filter_title_qs | Q(referenceanalytic__source__title_serial=title)
            # by default filter by LILACS express references
            object_list = object_list.filter(filter_title_qs)
            if self.actions['filter_status'] == '':
                self.actions['filter_status'] = 0
                object_list = object_list.filter(status=0)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(BiblioRefGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')
        source_id = self.request.GET.get('source')

        context['actions'] = self.actions
        context['document_type'] = self.request.GET.get('document_type')
        context['source_id'] = self.request.GET.get('source')
        context['user_role'] = user_role
        if source_id:
            context['reference_source'] = ReferenceSource.objects.get(pk=source_id)

        return context


# ========================= BiblioRef ========================================================

class BiblioRefListView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic references
    """
    model = Reference


class BiblioRefListSourceView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic references
    """
    model = ReferenceSource


class BiblioRefListAnalyticView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic references
    """
    model = ReferenceAnalytic


class BiblioRefUpdate(LoginRequiredView):
    """
    Handle creation and update of bibliographic references
    """

    success_url = reverse_lazy('list_biblioref')

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_thematic = ResourceThematicFormSet(self.request.POST, instance=self.object)
        formset_attachment = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        formset_library = LibraryFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_thematic_valid = formset_thematic.is_valid()
        formset_attachment_valid = formset_attachment.is_valid()
        formset_library_valid = formset_library.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(form,
                                                         [formset_descriptor, formset_thematic])

        if (form_valid and formset_descriptor_valid and formset_thematic_valid and
            formset_attachment_valid and valid_for_publication):

                self.object = form.save()
                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_thematic.instance = self.object
                formset_thematic.save()

                formset_attachment.instance = self.object
                formset_attachment.save()

                formset_library.instance = self.object
                formset_library.save()

                # update solr index
                # form.save()
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            # if not valid for publication return status to original (previous) value
            if not valid_for_publication:
                self.object.status = self.object.previous_value('status')
                self.request.POST['status'] = self.object.previous_value('status')

            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_descriptor=formset_descriptor,
                                                 formset_thematic=formset_thematic,
                                                 formset_attachment=formset_attachment,
                                                 formset_library=formset_library,
                                                 valid_for_publication=valid_for_publication))

    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(BiblioRefUpdate, self).get_form_kwargs()
        document_type = ''
        reference_source = None

        source_id = self.request.GET.get('source', None)

        # new analytic
        if source_id:
            reference_source = ReferenceSource.objects.get(pk=source_id)
            literature_type = reference_source.literature_type
            if literature_type == 'S':
                document_type = 'Sas'
            else:
                document_type = "{0}am".format(literature_type)

        # edition/new source
        else:
            # source/analytic edition
            if self.object:
                document_type = "{0}{1}".format(self.object.literature_type, self.object.treatment_level)
            # new source
            else:
                document_type = self.request.GET.get('document_type')

        # get list of fields allowed by document_type
        fieldsets = FIELDS_BY_DOCUMENT_TYPE.get(document_type, None)

        user_data = additional_user_info(self.request)

        additional_form_parameters = {}
        additional_form_parameters['user'] = self.request.user
        additional_form_parameters['user_data'] = user_data
        additional_form_parameters['fieldsets'] = fieldsets
        additional_form_parameters['document_type'] = document_type
        additional_form_parameters['reference_source'] = reference_source

        kwargs.update(additional_form_parameters)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BiblioRefUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        if user_role == 'editor_llxp':
            context['user_can_edit'] = True if not self.object or (self.object.status != 1 and self.object.cooperative_center_code == user_data['user_cc']) else False
            context['user_can_change_status'] = False
        elif user_role == 'doc':
            context['user_can_edit'] = True if not self.object or self.object.status == 0 or user_data['is_owner'] else False
            context['user_can_change_status'] = False
        else:
            context['user_can_edit'] = True
            context['user_can_change_status'] = True

        context['settings'] = settings
        context['help_fields'] = get_help_fields('biblioref')

        if self.object:
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        if self.request.method == 'GET':
            # special treatment for user of type documentalist is edit document from other user
            # add in the context list of descriptor and thematic already set for the document
            if user_role == 'doc' and self.object:
                c_type = ContentType.objects.get_for_model(self.get_object())

                context['descriptor_list'] = Descriptor.objects.filter(
                    object_id=self.object.id, content_type=c_type).exclude(created_by_id=user_id)
                context['thematic_list'] = ResourceThematic.objects.filter(
                    object_id=self.object.id, content_type=c_type).exclude(created_by_id=user_id)

                pending_descriptor_from_user = Descriptor.objects.filter(
                    created_by_id=self.request.user.id)
                pending_thematic_from_user = ResourceThematic.objects.filter(
                    created_by_id=user_id)

                context['formset_descriptor'] = DescriptorFormSet(instance=self.object,
                                                                  queryset=pending_descriptor_from_user)
                context['formset_thematic'] = ResourceThematicFormSet(instance=self.object,
                                                                      queryset=pending_thematic_from_user)
            else:
                context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
                context['formset_thematic'] = ResourceThematicFormSet(instance=self.object)

            context['formset_attachment'] = AttachmentFormSet(instance=self.object)
            context['formset_library'] = LibraryFormSet(instance=self.object,
                                                        queryset=ReferenceLocal.objects.filter(cooperative_center_code=user_data['user_cc']))

        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')

        if user_role == 'editor_llxp':
            redirect_url = "%s?document_type=S" % reverse_lazy('list_biblioref_sources')
        else:
            redirect_url = self.success_url

        return redirect_url



class BiblioRefSourceUpdateView(BiblioRefUpdate, UpdateView):
    """
    Used as class view to update BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceSource
    form_class = BiblioRefSourceForm


class BiblioRefAnaliticUpdateView(BiblioRefUpdate, UpdateView):
    """
    Used as class view to update BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceAnalytic
    form_class = BiblioRefAnalyticForm

    def get_context_data(self, **kwargs):
        # add source to context of form to present source information
        context = super(BiblioRefAnaliticUpdateView, self).get_context_data(**kwargs)
        context['reference_source'] = self.object.source

        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        return '/bibliographic/analytics?source=%s' % self.object.source.id


class BiblioRefSourceCreateView(BiblioRefUpdate, CreateView):
    """
    Used as class view to create BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceSource
    form_class = BiblioRefSourceForm

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        return 'new-analytic?source=%s' % self.object.pk


class BiblioRefAnalyticCreateView(BiblioRefUpdate, CreateView):
    """
    Used as class view to create BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceAnalytic
    form_class = BiblioRefAnalyticForm

    def get_context_data(self, **kwargs):
        # add source to context of form to present source information
        context = super(BiblioRefAnalyticCreateView, self).get_context_data(**kwargs)
        source_id = self.request.GET.get('source', None)

        if source_id:
            reference_source = ReferenceSource.objects.get(pk=source_id)
            context['reference_source'] = reference_source

        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        source_id = self.request.GET.get('source', None)
        return 'analytics?source=%s' % source_id

class SelectDocumentTypeView(FormView):
    template_name = 'biblioref/select_document_type.html'
    form_class = SelectDocumentTypeForm


class BiblioRefDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of BiblioRef objects
    """
    model = Reference
    success_url = reverse_lazy('list_biblioref')

    def get_object(self, queryset=None):
        obj = super(BiblioRefDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(BiblioRefDeleteView, self).get_object()
        child_class = obj.child_class()
        c_type = ContentType.objects.get_for_model(child_class)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ReferenceLocal.objects.filter(source=obj.id).delete()

        return super(BiblioRefDeleteView, self).delete(request, *args, **kwargs)

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')

        if user_role == 'editor_llxp':
            redirect_url = "%s?document_type=S" % reverse_lazy('list_biblioref_sources')
        else:
            redirect_url = self.success_url

        return redirect_url


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


@csrf_exempt
def field_assist(request, **kwargs):

    # add search_path to override deform templates
    deform_templates = resource_filename('deform', 'templates')
    search_path = ('templates/deform', deform_templates)
    deform.Form.set_zpt_renderer(search_path)

    field_name = kwargs.get('field_name')
    # get previous value from field (json)
    field_value = request.POST.get('field_value', '')
    field_id = request.POST.get('field_id', field_name)

    formid = request.POST.get('__formid__', '')

    field_name_camelcase = field_name.title().replace('_', '')
    field_full_classname = 'biblioref.field_definitions.{0}'.format(field_name_camelcase)

    field_definition = get_class(field_full_classname)

    appstruct = None
    field_json = None
    min_len_param = 1
    # if previous_value allow delete the first ocurrence
    if field_value and field_value != '[]':
        min_len_param = 0

    class Schema(colander.MappingSchema):
        data = field_definition()

    schema = Schema()
    form = deform.Form(schema, buttons=[deform.Button('submit', _('Save'),
                       css_class='btn btn-primary btn-large')], use_ajax=False)
    form['data'].widget = deform.widget.SequenceWidget(min_len=min_len_param, orderable=True)

    # check if is a submit of deform form
    if request.method == 'POST' and formid == 'deform':
        controls = parse_qsl(request.body, keep_blank_values=True)
        try:
            # If all goes well, deform returns a simple python structure of
            # the data. You use this same structure to populate a form with
            # data from permanent storage
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            # The exception contains a reference to the form object
            rendered = e.render()
        else:
            # form validated - create field_json with content and return to form render
            field_json = json.dumps(appstruct)
            rendered = form.render(appstruct)

    # otherwise is the open assist popup with or without field value
    else:
        if field_value:
            # add wrap element (data) to json
            field_value = '{"data" : %s}' % field_value
            appstruct = json.loads(field_value)

            rendered = form.render(appstruct)
        else:
            # new reference
            rendered = form.render()

    return render_to_response('biblioref/field_assist.html', {
        'form': rendered,
        'field_json': field_json,
        'field_name': field_name,
        'field_id': field_id,
        'deform_dependencies': form.get_widget_resources()
    })
