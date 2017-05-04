#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType

from django.shortcuts import render_to_response

from utils.views import ACTIONS
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info
from attachments.models import Attachment
from main.models import Descriptor
from help.models import get_help_fields
from utils.views import LoginRequiredView, GenericUpdateWithOneFormset
from datetime import datetime
from forms import *

import json


class OERGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for educational resources objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    context_object_name = "oer_list"
    search_field = "title"
    restrict_by_user = True

    def dispatch(self, *args, **kwargs):
        return super(OERGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('OER')

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        search_field = self.search_field + '__icontains'

        # search by field
        search = self.actions['s']
        if ':' in search:
            search_parts = search.split(':')
            search_field = search_parts[0] + '__icontains'
            search = search_parts[1]

        if search:
            object_list = self.model.objects.filter(**{search_field: search})
        else:
            object_list = self.model.objects.all()

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # filter by user
        if self.restrict_by_user and self.actions['filter_owner'] != "*":
            object_list = object_list.filter(created_by=self.request.user)

        # filter by cooperative center
        elif self.actions['filter_owner'] == 'center':
            user_cc = self.request.user.profile.get_attribute('cc')
            object_list = object_list.filter(cooperative_center_code=user_cc)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(OERGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('OER')

        context['actions'] = self.actions
        context['user_role'] = user_role

        return context


# ========================= Open Educational Resource ========================================================

class OERListView(OERGenericListView, ListView):
    """
    Extend OERGenericListView to list records
    """
    model = OER


class OERUpdate(LoginRequiredView):
    """
    Handle creation and update of educational resource
    """

    model = OER
    success_url = reverse_lazy('list_oer')
    form_class = OERForm

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_url = URLFormSet(self.request.POST, instance=self.object)
        formset_attachment = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        formset_thematic = ResourceThematicFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_attachment_valid = formset_attachment.is_valid()
        formset_thematic_valid = formset_thematic.is_valid()
        formset_url_valid = formset_url.is_valid()

        user_data = additional_user_info(self.request)
        # run cross formsets validations
        valid_for_publication = is_valid_for_publication(form,
                                                         [formset_descriptor, formset_thematic])

        if (form_valid and formset_descriptor_valid and formset_url_valid and formset_thematic_valid and
           formset_attachment_valid and valid_for_publication):

                self.object = form.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_attachment.instance = self.object
                formset_attachment.save()

                formset_url.instance = self.object
                formset_url.save()

                formset_thematic.instance = self.object
                formset_thematic.save()

                # update solr index
                # form.save()
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_descriptor=formset_descriptor,
                                                 formset_attachment=formset_attachment,
                                                 formset_url=formset_url,
                                                 formset_thematic=formset_thematic,
                                                 valid_for_publication=valid_for_publication))

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(OERUpdate, self).get_form_kwargs()

        user_data = additional_user_info(self.request)
        kwargs.update({'user': self.request.user, 'user_data': user_data})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(OERUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('OER')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        if user_role == 'doc':
            context['user_can_edit'] = True if not self.object or self.object.created_by == self.request.user else False
            context['user_can_change_status'] = False
        else:
            context['user_can_edit'] = True
            context['user_can_change_status'] = True

        context['settings'] = settings
        context['help_fields'] = get_help_fields('oer')
        context['indexing_fields'] = ['local_descriptors', 'local_geo_descriptors', 'institution_as_subject']

        if self.object:
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        if self.request.method == 'GET':
            context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
            context['formset_attachment'] = AttachmentFormSet(instance=self.object)
            context['formset_url'] = URLFormSet(instance=self.object)
            context['formset_thematic'] = ResourceThematicFormSet(instance=self.object)

        return context


class OERUpdateView(OERUpdate, UpdateView):
    """
    Used as class view to update Act
    Extend OERUpdate that do all the work
    """


class OERCreateView(OERUpdate, CreateView):
    """
    Used as class view to create Act
    Extend OERUpdate that do all the work
    """


class OERDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of BiblioRef objects
    """
    model = OER
    success_url = reverse_lazy('list_oer')

    def get_object(self, queryset=None):
        obj = super(OERDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(OERDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(OERDeleteView, self).delete(request, *args, **kwargs)


# ========================= ACT TYPE AUX LIST ============================================
class OERTypeListView(OERListView, ListView):
    """
    List Aux OER Type
    """
    model = OERType
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False


class OERTypeUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act scope
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = OERType
    success_url = reverse_lazy('list_act_type')
    formset = OERTypeTranslationFormSet
    fields = '__all__'


class OERTypeUpdateView(OERTypeUpdate, UpdateView):
    """
    Used as class view for update act scope
    Extend Update class that do all the work
    """


class OERTypeCreateView(OERTypeUpdate, CreateView):
    """
    Used as class view for create act scope
    Extend Update class that do all the work
    """


class OERTypeDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act scope
    """
    model = OERType
    success_url = reverse_lazy('list_oer_type')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(OERTypeDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj
