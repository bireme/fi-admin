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
from utils.views import LoginRequiredView
from datetime import datetime
from forms import *

import json


class LeisRefGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for legislation records objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    context_object_name = "act_list"
    search_field = "act_number"

    def dispatch(self, *args, **kwargs):
        return super(LeisRefGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LeisRef')

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

        # filter by user
        if not self.actions['filter_owner'] or self.actions['filter_owner'] == 'user':
            object_list = object_list.filter(created_by=self.request.user)
        # filter by cooperative center
        elif self.actions['filter_owner'] == 'center':
            user_cc = self.request.user.profile.get_attribute('cc')
            object_list = object_list.filter(cooperative_center_code=user_cc)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(LeisRefGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LeisRef')

        context['actions'] = self.actions
        context['user_role'] = user_role

        return context


# ========================= LeisRef ========================================================

class LeisRefListView(LeisRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list legislation records
    """
    model = Act


class LeisRefActListView(ListView):
    """
    List legislation records (used by relationship popup selection window)
    """
    model = Act
    template_name = "leisref/act_related.html"
    paginate_by = 10
    context_object_name = "act_list"

    def get_queryset(self):

        param_region = self.request.GET.get('region')
        param_type = self.request.GET.get('type')
        param_year = self.request.GET.get('year')
        param_number = self.request.GET.get('number')

        object_list = self.model.objects.filter(scope_region_id=param_region)
        if param_type:
            object_list = object_list.filter(act_type=param_type)
        if param_number:
            object_list = object_list.filter(act_number__startswith=param_number)
        if param_year:
            object_list = object_list.filter(issue_date__year=param_year)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(LeisRefActListView, self).get_context_data(**kwargs)

        region_id = self.request.GET.get('region')

        context['param_region'] = region_id
        context['param_type'] = self.request.GET.get('type', '')
        context['param_number'] = self.request.GET.get('number', '')
        context['param_year'] = self.request.GET.get('year', '')
        context['param_added'] = self.request.GET.get('added', '')
        context['act_type_select'] = ActType.objects.filter(scope_region=region_id)

        return context


class LeisRefUpdate(LoginRequiredView):
    """
    Handle creation and update of bibliographic records
    """

    model = Act
    success_url = reverse_lazy('list_legislation')
    form_class = ActForm

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_url = URLFormSet(self.request.POST, instance=self.object)
        formset_attachment = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        formset_relation = RelationFormSet(self.request.POST, instance=self.object)
        formset_thematic = ResourceThematicFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_attachment_valid = formset_attachment.is_valid()
        formset_thematic_valid = formset_thematic.is_valid()
        formset_relation_valid = formset_relation.is_valid()
        formset_url_valid = formset_url.is_valid()

        user_data = additional_user_info(self.request)
        # run cross formsets validations
        valid_for_publication = is_valid_for_publication(form,
                                                         [formset_descriptor, formset_thematic])

        if (form_valid and formset_descriptor_valid and formset_url_valid and formset_thematic_valid and
           formset_attachment_valid and formset_relation_valid and valid_for_publication):

                self.object = form.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_attachment.instance = self.object
                formset_attachment.save()

                formset_url.instance = self.object
                formset_url.save()

                formset_relation.instance = self.object
                formset_relation.save()

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
                                                 formset_relation=formset_relation,
                                                 formset_thematic=formset_thematic,
                                                 valid_for_publication=valid_for_publication))

    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(LeisRefUpdate, self).get_form_kwargs()

        user_data = additional_user_info(self.request)
        kwargs.update({'user': self.request.user, 'user_data': user_data})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(LeisRefUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LeisRef')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        if user_role == 'doc':
            context['user_can_edit'] = True if not self.object or self.object.status == 0 or (self.object.status != 1 and self.object.cooperative_center_code == user_data['user_cc']) else False
            context['user_can_change_status'] = False
        else:
            context['user_can_edit'] = True
            context['user_can_change_status'] = True

        context['settings'] = settings
        context['help_fields'] = get_help_fields('leisref')
        context['indexing_fields'] = ['local_descriptors', 'local_geo_descriptors', 'institution_as_subject']

        if self.object:
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        if self.request.method == 'GET':
            context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
            context['formset_attachment'] = AttachmentFormSet(instance=self.object)
            context['formset_url'] = URLFormSet(instance=self.object)
            context['formset_relation'] = RelationFormSet(instance=self.object)
            context['formset_thematic'] = ResourceThematicFormSet(instance=self.object)

        if self.object:
            context['passive_relationship'] = ActRelationship.objects.filter(act_referred=self.object)


        return context


class ActUpdateView(LeisRefUpdate, UpdateView):
    """
    Used as class view to update Act
    Extend LeisRefUpdate that do all the work
    """


class ActCreateView(LeisRefUpdate, CreateView):
    """
    Used as class view to create Act
    Extend LeisRefUpdate that do all the work
    """


class ActDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of BiblioRef objects
    """
    model = Act
    success_url = reverse_lazy('list_legislation')

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
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(BiblioRefDeleteView, self).delete(request, *args, **kwargs)


def context_lists(request, region_id):
    """
    Receive source and field name and display help text
    """

    type_list = [dict({'value': t.id, 'name': unicode(t)}) for t in ActType.objects.filter(scope_region=region_id)]
    type_list = dict({'type_list': type_list})
    scope_list = [dict({'value': s.id, 'name': unicode(s)}) for s in ActScope.objects.filter(scope_region=region_id)]
    scope_list = dict({'scope_list': scope_list})
    source_list = [dict({'value': s.id, 'name': unicode(s)}) for s in ActSource.objects.filter(scope_region=region_id)]
    source_list = dict({'source_list': source_list})
    organ_issuer_list = [dict({'value': s.id, 'name': unicode(s)}) for s in ActOrganIssuer.objects.filter(scope_region=region_id)]
    organ_issuer_list = dict({'organ_issuer_list': organ_issuer_list})
    relation_list = [dict({'value': r.id, 'name': unicode(r)}) for r in ActRelationType.objects.filter(scope_region=region_id)]
    relation_list = dict({'relation_list': relation_list})
    # join all lists
    context_lists = dict(type_list.items() + scope_list.items() + source_list.items() + organ_issuer_list.items() + relation_list.items())

    data = simplejson.dumps(context_lists)

    return HttpResponse(data, content_type='application/json')

@login_required
def add_related_act(request):
    """
    Add act with minimum fields for relationship
    """
    success_url = ''
    if request.method == 'POST':
        form = ActRelatedForm(request.POST)
        region_id = request.POST.get('scope_region')
        added = 1
        if form.is_valid():
            new_act = form.save()
            success_url = "{0}/?region={1}&number={2}".format(reverse_lazy('act_related'),
                                                              region_id, new_act.act_number)
        else:
            success_url = "{0}/?region={1}&added=0".format(reverse_lazy('act_related'),
                                                           region_id)

    return HttpResponseRedirect(success_url)
