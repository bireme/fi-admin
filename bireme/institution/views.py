#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.db.models import Q

from utils.views import ACTIONS
from utils.context_processors import additional_user_info
from help.models import get_help_fields
from utils.views import LoginRequiredView, GenericUpdateWithOneFormset
from datetime import datetime
from forms import *

class InstGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for legislation records objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    context_object_name = "inst_list"
    search_field = "name"

    def dispatch(self, *args, **kwargs):
        return super(InstGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')

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

        object_list = self.model.objects.filter(**{search_field: search})

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # filter by institution of user
        if self.actions['filter_owner'] != "*":
            object_list = object_list.filter(cooperative_center_code=user_data['user_cc'])

        return object_list

    def get_context_data(self, **kwargs):
        context = super(InstGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')

        context['actions'] = self.actions
        context['user_role'] = user_role

        return context


# ========================= Institution ========================================================

class InstListView(InstGenericListView, ListView):
    """
    Extend InstGenericListView to list records
    """
    model = Institution


class InstUpdate(LoginRequiredView):
    """
    Handle creation and update
    """
    model = Institution
    success_url = reverse_lazy('list_institution')
    form_class = InstitutionForm

    def form_valid(self, form):
        formset_person = PersonFormSet(self.request.POST, instance=self.object)
        formset_phone = PhoneFormSet(self.request.POST, instance=self.object)
        formset_email = EmailFormSet(self.request.POST, instance=self.object)
        formset_url = URLFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_person_valid = formset_person.is_valid()
        formset_phone_valid = formset_phone.is_valid()
        formset_email_valid = formset_email.is_valid()
        formset_url_valid = formset_url.is_valid()

        user_data = additional_user_info(self.request)

        if (form_valid and formset_person_valid and formset_phone_valid and
            formset_email_valid and formset_url_valid):

                self.object = form.save()

                formset_person.instance = self.object
                formset_person.save()

                formset_phone.instance = self.object
                formset_phone.save()

                formset_email.instance = self.object
                formset_email.save()

                formset_url.instance = self.object
                formset_url.save()

                # save metadata
                form.save()

                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_person=formset_person,
                                                 formset_phone=formset_phone,
                                                 formset_email=formset_email,
                                                 formset_url=formset_url))


    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(InstUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        context['user_can_edit'] = True if not self.object or self.object.cooperative_center_code in ['BR1.1', user_data['user_cc']] else False
        if user_role == 'doc':
            context['user_can_change_status'] = False
        else:
            context['user_can_change_status'] = True

        context['settings'] = settings
        context['help_fields'] = get_help_fields('institution')

        if self.object:
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        if self.request.method == 'GET':
            context['formset_person'] = PersonFormSet(instance=self.object)
            context['formset_phone'] = PhoneFormSet(instance=self.object)
            context['formset_email'] = EmailFormSet(instance=self.object)
            context['formset_url'] = URLFormSet(instance=self.object)

        return context


class InstUpdateView(InstUpdate, UpdateView):
    """
    Used as class view to update Institution
    Extend InstUpdate that do all the work
    """

class InstCreateView(InstUpdate, CreateView):
    """
    Used as class view to create Institution
    Extend InstUpdate that do all the work
    """


class InstDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete objects
    """
    model = Institution
    success_url = reverse_lazy('list_institution')

    def get_object(self, queryset=None):
        obj = super(InstDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(InstDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        ContactPerson.objects.filter(institution_id=obj.id).delete()
        ContactPhone.objects.filter(institution_id=obj.id).delete()
        ContactEmail.objects.filter(institution_id=obj.id).delete()
        URL.objects.filter(institution_id=obj.id).delete()

        return super(InstDeleteView, self).delete(request, *args, **kwargs)
