#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render_to_response

from utils.views import ACTIONS
from utils.context_processors import additional_user_info
from attachments.models import Attachment
from main.models import Descriptor
from help.models import get_help_fields
from utils.views import LoginRequiredView, GenericUpdateWithOneFormset
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
    restrict_by_user = True

    def dispatch(self, *args, **kwargs):
        return super(LeisRefGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LeisRef')

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        search_field = self.search_field + '__exact'

        # search by field
        search = self.actions['s']
        if ':' in search:
            search_parts = search.split(':')
            search_field = search_parts[0] + '__icontains'
            search = search_parts[1]

        filter_qs = Q(**{search_field: search})
        # if Act model search also by title and denomination fields
        if self.search_field == 'act_number':
            filter_qs =  filter_qs | Q(title__icontains=search) | Q(denomination__icontains=search)

        object_list = self.model.objects.filter(filter_qs)
        # filter by status
        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])
        # filter by scope region country
        if self.actions['filter_country'] != '':
            object_list = object_list.filter(scope_region=self.actions['filter_country'])
        # filter by indexed database
        if self.actions['filter_indexed_database'] != '':
            object_list = object_list.filter(indexed_database=self.actions['filter_indexed_database'])
        # filter by act_type
        if self.actions['filter_act_type'] != '':
            object_list = object_list.filter(act_type=self.actions['filter_act_type'])

        # order
        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # filter by user
        if self.restrict_by_user and self.actions['filter_owner'] != "*":
            object_list = object_list.filter(created_by=self.request.user)

        if self.actions['results_per_page'] != '':
            self.paginate_by = self.actions['results_per_page']

        return object_list

    def get_context_data(self, **kwargs):
        context = super(LeisRefGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LeisRef')
        show_advaced_filters = self.request.GET.get('apply_filters', False)
        scope_region_list = ActCountryRegion.objects.all().order_by('name')
        indexed_database_list = Database.objects.all().order_by('name')
        act_type_list = ActType.objects.all().order_by('name')

        context['actions'] = self.actions
        context['user_role'] = user_role
        context['scope_region_list'] = scope_region_list
        context['show_advaced_filters'] = show_advaced_filters
        context['indexed_database_list'] = indexed_database_list
        context['act_type_list'] = act_type_list

        return context


# ========================= LeisRef ========================================================

class LeisRefListView(LeisRefGenericListView, ListView):
    """
    Extend LeisRefGenericListView to list legislation records
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
        object_list = []

        if param_region:
            object_list = self.model.objects.filter(scope_region_id=param_region)
        else:
            object_list = self.model.objects.all()

        if param_type:
            object_list = object_list.filter(act_type=param_type)
        if param_number:
            object_list = object_list.filter(act_number__startswith=param_number)
        if param_year:
            object_list = object_list.filter(issue_date__year=param_year)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(LeisRefActListView, self).get_context_data(**kwargs)
        act_type_list = []

        param_region = self.request.GET.get('region')

        context['param_region'] = param_region
        context['param_type'] = self.request.GET.get('type', '')
        context['param_number'] = self.request.GET.get('number', '')
        context['param_year'] = self.request.GET.get('year', '')
        context['param_added'] = self.request.GET.get('added', '')
        context['act_type_select'] = ActType.objects.all()

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

        if (form_valid and formset_descriptor_valid and formset_url_valid and formset_thematic_valid and
           formset_attachment_valid and formset_relation_valid):

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

                # save many-to-many relation fields
                form.save_m2m()
                # update solr index
                form.save()

                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_descriptor=formset_descriptor,
                                                 formset_attachment=formset_attachment,
                                                 formset_url=formset_url,
                                                 formset_relation=formset_relation,
                                                 formset_thematic=formset_thematic))

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
    Handle delete of Act objects
    """
    model = Act
    success_url = reverse_lazy('list_legislation')

    def get_object(self, queryset=None):
        obj = super(ActDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(ActDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(ActDeleteView, self).delete(request, *args, **kwargs)


def check_duplication(request, act_type, act_number):
    """
    Receive source and field name and display help text
    """
    dup_list = []
    dup_list = [dict({'id': act.id, 'title': unicode(act)}) for act in Act.objects.filter(act_type=act_type,
                                                                                         act_number=act_number)]

    data = simplejson.dumps(dup_list)

    return HttpResponse(data, content_type='application/json')


def context_lists(request, region_id):

    # act type
    type_objects = [(s.id, unicode(s)) for s in ActType.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
    type_objects.sort(key=lambda tup: tup[1])
    type_list = [dict({'value': t[0], 'name': t[1]}) for t in type_objects]
    type_list = dict({'type_list': type_list})

    # act scopes
    scope_objects = [(s.id, unicode(s)) for s in ActScope.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
    scope_objects.sort(key=lambda tup: tup[1])
    scope_list = [dict({'value': s[0], 'name':s[1]}) for s in scope_objects]
    scope_list = dict({'scope_list': scope_list})

    # act sources
    source_objects = [(s.id, unicode(s)) for s in ActSource.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
    source_objects.sort(key=lambda tup: tup[1])
    source_list = [dict({'value': s[0], 'name': s[1]}) for s in source_objects]
    source_list = dict({'source_list': source_list})

    # act organ_issuer
    organ_issuer_objects = [(s.id, unicode(s)) for s in ActOrganIssuer.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
    organ_issuer_objects.sort(key=lambda tup: tup[1])
    organ_issuer_list = [dict({'value': s[0], 'name': s[1]}) for s in organ_issuer_objects]
    organ_issuer_list = dict({'organ_issuer_list': organ_issuer_list})

    # act relation types
    relation_objects = [(s.id, unicode(s)) for s in ActRelationType.objects.filter(Q(scope_region=None) | Q(scope_region=region_id))]
    relation_objects.sort(key=lambda tup: tup[1])
    relation_list = [dict({'value': r[0], 'name': r[1]}) for r in relation_objects]
    relation_list = dict({'relation_list': relation_list})

    # act scope state
    state_objects = [(s.id, unicode(s)) for s in ActState.objects.filter(scope_region=region_id)]
    state_objects.sort(key=lambda tup: tup[1])
    state_list = [dict({'value': r[0], 'name': r[1]}) for r in state_objects]
    state_list = dict({'state_list': state_list})

    # act scope city
    city_objects = [(s.id, unicode(s)) for s in ActCity.objects.filter(scope_region=region_id)]
    city_objects.sort(key=lambda tup: tup[1])
    city_list = [dict({'value': r[0], 'name': r[1]}) for r in city_objects]
    city_list = dict({'city_list': city_list})

    # act collection
    collection_objects = [(s.id, unicode(s)) for s in ActCollection.objects.all()]
    collection_objects.sort(key=lambda tup: tup[1])
    collection_list = [dict({'value': r[0], 'name': r[1]}) for r in collection_objects]
    collection_list = dict({'collection_list': collection_list})

    # join all lists
    context_lists = dict(type_list.items() + scope_list.items() + source_list.items() +
                         organ_issuer_list.items() + relation_list.items() + state_list.items() +
                         city_list.items() + collection_list.items() )

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


# ========================= COUNTRY REGION AUX LIST ============================================
class CountryRegionListView(LeisRefListView, ListView):
    """
    List Aux Contry Region
    """
    model = ActCountryRegion
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False


class CountryRegionUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of MediaType objects
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActCountryRegion
    success_url = reverse_lazy('list_country_region')
    formset = CountryRegionTranslationFormSet
    fields = '__all__'


class CountryRegionUpdateView(CountryRegionUpdate, UpdateView):
    """
    Used as class view for update media type
    Extend MediaTypeUpdate that do all the work
    """


class CountryRegionCreateView(CountryRegionUpdate, CreateView):
    """
    Used as class view for create media type
    Extend MediaTypeUpdate that do all the work
    """


class CountryRegionDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of MediaType objects
    """
    model = ActCountryRegion
    success_url = reverse_lazy('list_country_region')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(CountryRegionDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj


# ========================= ACT SCOPE AUX LIST ============================================
class ActScopeListView(LeisRefListView, ListView):
    """
    List Aux Act Scope
    """
    model = ActScope
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False


class ActScopeUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act scope
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActScope
    success_url = reverse_lazy('list_act_scope')
    formset = ActScopeTranslationFormSet
    fields = '__all__'


class ActScopeUpdateView(ActScopeUpdate, UpdateView):
    """
    Used as class view for update act scope
    Extend Update class that do all the work
    """


class ActScopeCreateView(ActScopeUpdate, CreateView):
    """
    Used as class view for create act scope
    Extend Update class that do all the work
    """


class ActScopeDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act scope
    """
    model = ActScope
    success_url = reverse_lazy('list_act_scope')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActScopeDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj

# ========================= ACT TYPE AUX LIST ============================================
class ActTypeListView(LeisRefListView, ListView):
    """
    List Aux Act Scope
    """
    model = ActType
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActTypeUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act scope
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActType
    success_url = reverse_lazy('list_act_type')
    formset = ActTypeTranslationFormSet
    fields = '__all__'


class ActTypeUpdateView(ActTypeUpdate, UpdateView):
    """
    Used as class view for update act scope
    Extend Update class that do all the work
    """


class ActTypeCreateView(ActTypeUpdate, CreateView):
    """
    Used as class view for create act scope
    Extend Update class that do all the work
    """


class ActTypeDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act scope
    """
    model = ActType
    success_url = reverse_lazy('list_act_type')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActTypeDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj


# ========================= ACT ORGAN ISSUER AUX LIST ============================================
class ActOrganListView(LeisRefListView, ListView):
    """
    List Aux Act Organ Issuer
    """
    model = ActOrganIssuer
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActOrganUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act scope
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActOrganIssuer
    success_url = reverse_lazy('list_act_organ')
    formset = ActOrganTranslationFormSet
    fields = '__all__'


class ActOrganUpdateView(ActOrganUpdate, UpdateView):
    """
    Used as class view for update act scope
    Extend update that do all the work
    """


class ActOrganCreateView(ActOrganUpdate, CreateView):
    """
    Used as class view for create act scope
    Extend update that do all the work
    """


class ActOrganDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act scope
    """
    model = ActOrganIssuer
    success_url = reverse_lazy('list_act_organ')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActOrganDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj


# ========================= ACT SOURCE AUX LIST ============================================
class ActSourceListView(LeisRefListView, ListView):
    """
    List Aux Act Organ Source
    """
    model = ActSource
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActSourceUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act source
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActSource
    success_url = reverse_lazy('list_act_source')
    formset = ActSourceTranslationFormSet
    fields = '__all__'


class ActSourceUpdateView(ActSourceUpdate, UpdateView):
    """
    Used as class view for update act source
    Extend update that do all the work
    """


class ActSourceCreateView(ActSourceUpdate, CreateView):
    """
    Used as class view for create act source
    Extend update that do all the work
    """


class ActSourceDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act source
    """
    model = ActSource
    success_url = reverse_lazy('list_act_source')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActSourceDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj


# ========================= ACT RELATION TYPE AUX LIST ============================================
class ActRelTypeListView(LeisRefListView, ListView):
    """
    List Aux Act Relation Type
    """
    model = ActRelationType
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActRelTypeUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act source
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActRelationType
    success_url = reverse_lazy('list_act_reltype')
    formset = ActRelTypeTranslationFormSet
    fields = '__all__'


class ActRelTypeUpdateView(ActRelTypeUpdate, UpdateView):
    """
    Used as class view for update act source
    Extend update that do all the work
    """


class ActRelTypeCreateView(ActRelTypeUpdate, CreateView):
    """
    Used as class view for create act source
    Extend update that do all the work
    """


class ActRelTypeDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act source
    """
    model = ActRelationType
    success_url = reverse_lazy('list_act_reltype')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActRelTypeDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj

# ========================= ACT SCOPE STATE AUX LIST ============================================
class ActStateListView(LeisRefListView, ListView):
    """
    List Aux Act Scope State
    """
    model = ActState
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActStateUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act source
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActState
    success_url = reverse_lazy('list_act_state')
    formset = ActStateTranslationFormSet
    fields = '__all__'


class ActStateUpdateView(ActStateUpdate, UpdateView):
    """
    Used as class view for update act source
    Extend update that do all the work
    """


class ActStateCreateView(ActStateUpdate, CreateView):
    """
    Used as class view for create act source
    Extend update that do all the work
    """


class ActStateDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act source
    """
    model = ActState
    success_url = reverse_lazy('list_act_state')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActStateDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj

# ========================= ACT SCOPE CITY AUX LIST ============================================
class ActCityListView(LeisRefListView, ListView):
    """
    List Aux Act Scope City
    """
    model = ActCity
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActCityUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act source
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActCity
    success_url = reverse_lazy('list_act_city')
    formset = ActCityTranslationFormSet
    fields = '__all__'


class ActCityUpdateView(ActCityUpdate, UpdateView):
    """
    Used as class view for update act source
    Extend update that do all the work
    """


class ActCityCreateView(ActCityUpdate, CreateView):
    """
    Used as class view for create act source
    Extend update that do all the work
    """


class ActCityDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act source
    """
    model = ActCity
    success_url = reverse_lazy('list_act_city')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActCityDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj

# ========================= ACT COLLECTION AUX LIST ============================================
class ActCollectionListView(LeisRefListView, ListView):
    """
    List Aux Act Collection
    """
    model = ActCollection
    context_object_name = "aux_list"
    search_field = "name"
    restrict_by_user = False
    paginate_by = 999


class ActCollectionUpdate(GenericUpdateWithOneFormset):
    """
    Handle creation and update of act source
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = ActCollection
    success_url = reverse_lazy('list_act_collection')
    formset = ActCollectionTranslationFormSet
    # exclude scope_region field of the list
    fields = ('name', 'language')


class ActCollectionUpdateView(ActCollectionUpdate, UpdateView):
    """
    Used as class view for update act source
    Extend update that do all the work
    """


class ActCollectionCreateView(ActCollectionUpdate, CreateView):
    """
    Used as class view for create act source
    Extend update that do all the work
    """


class ActCollectionDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of act source
    """
    model = ActCollection
    success_url = reverse_lazy('list_act_collection')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(ActCollectionDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj
