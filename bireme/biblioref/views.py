#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from deform.exception import ValidationFailure

from field_definitions import FIELDS_BY_DOCUMENT_TYPE

from utils.views import ACTIONS
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info
from main.models import Descriptor
from utils.views import LoginRequiredView
from urlparse import parse_qsl
from forms import *

import colander
import deform
import json

class BiblioRefGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for bibliographic references objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    restrict_by_user = True

    def dispatch(self, *args, **kwargs):
        return super(BiblioRefGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # getting action parameter        
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        search_field = self.search_field + '__contains'

        object_list = self.model.objects.filter(**{search_field: self.actions['s']})

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        if self.restrict_by_user and self.actions['filter_owner'] != "*":
            object_list = object_list.filter(created_by=self.request.user)
        elif self.actions['filter_owner'] == "*":
            # restrict by cooperative center
            user_cc = self.request.user.profile.get_attribute('cc')
            object_list = object_list.filter(cooperative_center_code=user_cc)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(BiblioRefGenericListView, self).get_context_data(**kwargs)
        context['actions'] = self.actions
        return context


# ========================= BiblioRef ========================================================

class BiblioRefListView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic references 
    """
    model = Reference
    context_object_name = "references"
    search_field = "title"

class BiblioRefUpdate(LoginRequiredView):
    """
    Handle creation and update of bibliographic references
    """
    model = Reference
    success_url = reverse_lazy('list_biblioref')
    form_class = BiblioRefForm

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_keyword = KeywordFormSet(self.request.POST, instance=self.object)
        formset_thematic = ResourceThematicFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_keyword_valid = formset_keyword.is_valid()

        # if document is created by other user assume formsets descriptor and thematic valid
        if self.object and (self.object.created_by != self.request.user):
            formset_descriptor_valid = True
            formset_thematic_valid = True
        else:
            formset_descriptor_valid = formset_descriptor.is_valid()
            formset_thematic_valid = formset_thematic.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(form,
                                          [formset_descriptor, formset_keyword, formset_thematic])


        if (form_valid and formset_descriptor_valid and formset_keyword_valid
                and formset_thematic_valid and valid_for_publication):

                self.object = form.save()
                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_keyword.instance = self.object
                formset_keyword.save()

                formset_thematic.instance = self.object
                formset_thematic.save()

                # update solr index
                form.save()
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                  formset_descriptor=formset_descriptor,
                                  formset_keyword=formset_keyword,
                                  formset_thematic=formset_thematic,
                                  valid_for_publication=valid_for_publication))


    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)


    def get_form_kwargs(self):
        kwargs = super(BiblioRefUpdate, self).get_form_kwargs()

        # document_type is passing via GET and is used to filter the list of form fields
        document_type = self.request.GET.get('document_type')
        # get list of fields allowed by document_type
        field_list = FIELDS_BY_DOCUMENT_TYPE.get(document_type, None)

        user_data = additional_user_info(self.request)

        additional_form_parameters = {}
        additional_form_parameters['user'] = self.request.user
        additional_form_parameters['user_data'] = user_data
        additional_form_parameters['field_list'] = field_list

        kwargs.update(additional_form_parameters)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BiblioRefUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('BiblioRef')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['role'] = user_role
        context['settings'] = settings

        if self.request.method == 'GET':
            # special treatment for user of type documentalist is edit document from other user
            # add in the context list of descriptor, keyword and thematic already set for the document
            if user_role == 'doc' and self.object:
                c_type = ContentType.objects.get_for_model(self.get_object())

                context['descriptor_list'] = Descriptor.objects.filter(
                    object_id=self.object.id, content_type=c_type).exclude(created_by_id=user_id, status=0)
                context['keyword_list'] = Keyword.objects.filter(
                    object_id=self.object.id, content_type=c_type).exclude(created_by_id=user_id, status=0)
                context['thematic_list'] = ResourceThematic.objects.filter(
                    object_id=self.object.id, content_type=c_type).exclude(created_by_id=user_id, status=0)

                pending_descriptor_from_user = Descriptor.objects.filter(
                    created_by_id=self.request.user.id, status=0)
                pending_keyword_from_user = Keyword.objects.filter(
                    created_by_id=user_id, status=0)
                pending_thematic_from_user = ResourceThematic.objects.filter(
                    created_by_id=user_id, status=0)

                context['formset_descriptor'] = DescriptorFormSet(instance=self.object,
                    queryset=pending_descriptor_from_user)
                context['formset_keyword'] = KeywordFormSet(instance=self.object,
                    queryset=pending_keyword_from_user)
                context['formset_thematic'] = ResourceThematicFormSet(instance=self.object,
                    queryset=pending_thematic_from_user)
            else:
                context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
                context['formset_keyword'] = KeywordFormSet(instance=self.object)
                context['formset_thematic'] = ResourceThematicFormSet(instance=self.object)

        return context


class BiblioRefUpdateView(BiblioRefUpdate, UpdateView):
    """
    Used as class view to update BiblioRef
    Extend BiblioRefUpdate that do all the work    
    """


class BiblioRefCreateView(BiblioRefUpdate, CreateView):
    """
    Used as class view to create BiblioRef
    Extend BiblioRefUpdate that do all the work
    """


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
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Keyword.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(BiblioRefDeleteView, self).delete(request, *args, **kwargs)


def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

@csrf_exempt
def field_assist(request, **kwargs):

    field_name = kwargs.get('field_name')
    # get previous value from field (json)
    field_value = request.POST.get('field_value', '')

    formid = request.POST.get('__formid__', '')

    field_name_camelcase = field_name.title().replace('_','')
    field_full_classname = 'biblioref.field_definitions.{0}'.format(field_name_camelcase)

    field_definition = get_class(field_full_classname)

    appstruct = None
    field_json = None    

    class Schema(colander.MappingSchema):
        data = field_definition()

    schema = Schema()
    form = deform.Form(schema, buttons=('submit',), use_ajax=True)
    form['data'].widget = deform.widget.SequenceWidget(min_len=1, orderable=True)


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
        'deform_dependencies': form.get_widget_resources()
    })
