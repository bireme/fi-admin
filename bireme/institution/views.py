#! coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.db.models import Q, Count

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
    search_field = "name"

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')
        user_type = user_data.get('user_type')
        # restrict institution module to advanced users with DirIns permission
        if user_type != 'advanced' or not user_role:
            return HttpResponseForbidden()

        return super(InstGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')
        user_cc = user_data.get('user_cc')
        user_type = user_data.get('user_type')

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        # search filter
        search = self.actions['s']
        search_filter = Q(name__icontains=search) | Q(cc_code__icontains=search) | Q(acronym__icontains=search)

        object_list = self.model.objects.filter(search_filter)

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        if self.actions['filter_country'] != '':
            object_list = object_list.filter(country=self.actions['filter_country'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # filter by institution of user
        if self.actions['filter_owner'] != "*" or user_cc != 'BR1.1':
            object_list = object_list.filter(cc_code=user_cc)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(InstGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')

        country_list = Institution.objects.values('country').distinct().annotate(total=Count('pk')).order_by('-total')
        for country in country_list:
            country_id = country['country']
            if country_id > 0:
                country['country_name'] = unicode(Country.objects.get(pk=country_id))


        context['actions'] = self.actions
        context['user_role'] = user_role
        context['user_cc'] = user_data.get('user_cc')
        context['country_list'] = country_list

        return context


# ========================= Institution ========================================================

class InstListView(InstGenericListView, ListView):
    """
    Extend InstGenericListView to list records
    """
    model = Institution

class UnitListView(ListView):
    model = Unit
    template_name = "institution/institution_unit.html"
    paginate_by = 10

    def get_queryset(self):

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        param_country = self.request.GET.get('country')

        search = self.actions['s']
        search_filter = Q(name__icontains=search) | Q(acronym__icontains=search)

        object_list = []

        if search:
            object_list = self.model.objects.filter(search_filter)
        else:
            object_list = self.model.objects.all()

        if param_country:
            object_list = object_list.filter(country=param_country)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(UnitListView, self).get_context_data(**kwargs)

        context['form'] = UnitForm()
        context['param_country'] = self.request.GET.get('country')
        context['actions'] = self.actions

        return context

class InstUpdate(LoginRequiredView):
    """
    Handle creation and update
    """
    model = Institution
    success_url = reverse_lazy('list_institution')
    form_class = InstitutionForm

    def get_object(self, *args, **kwargs):
        obj = super(InstUpdate, self).get_object(*args, **kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')
        user_cc = user_data.get('user_cc')
        user_type = user_data.get('user_type')

        # restrict edition to BR1.1 users or advanced users with same CC code
        if user_cc != 'BR1.1':
            if user_cc != obj.cc_code or user_type != 'advanced':
                return None

        return obj

    def form_valid(self, form):
        formset_person = PersonFormSet(self.request.POST, instance=self.object)
        formset_phone = PhoneFormSet(self.request.POST, instance=self.object)
        formset_email = EmailFormSet(self.request.POST, instance=self.object)
        formset_url = URLFormSet(self.request.POST, instance=self.object)
        formset_unitlevel = UnitLevelFormSet(self.request.POST, instance=self.object)
        formset_adm = AdmFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_person_valid = formset_person.is_valid()
        formset_phone_valid = formset_phone.is_valid()
        formset_email_valid = formset_email.is_valid()
        formset_url_valid = formset_url.is_valid()
        formset_unitlevel_valid = formset_unitlevel.is_valid()
        formset_adm_valid = formset_adm.is_valid()

        user_data = additional_user_info(self.request)

        if (form_valid and formset_person_valid and formset_phone_valid and
            formset_email_valid and formset_url_valid and formset_unitlevel_valid and
            formset_adm_valid):

                self.object = form.save()

                formset_person.instance = self.object
                formset_person.save()

                formset_phone.instance = self.object
                formset_phone.save()

                formset_email.instance = self.object
                formset_email.save()

                formset_url.instance = self.object
                formset_url.save()

                formset_unitlevel.instance = self.object
                formset_unitlevel.save()

                formset_adm.instance = self.object
                formset_adm.save()

                # update solr index
                form.save()
                # save many-to-many relation fields
                form.save_m2m()

                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_person=formset_person,
                                                 formset_phone=formset_phone,
                                                 formset_email=formset_email,
                                                 formset_url=formset_url,
                                                 formset_adm=formset_adm,
                                                 formset_unitlevel=formset_unitlevel))


    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)


    def get_form_kwargs(self):
        kwargs = super(InstUpdate, self).get_form_kwargs()

        user_data = additional_user_info(self.request)

        additional_form_parameters = {}
        additional_form_parameters['user_data'] = user_data

        kwargs.update(additional_form_parameters)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(InstUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('DirIns')
        user_cc = user_data['user_cc']
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        context['user_can_edit'] = True if not self.object or self.object.cooperative_center_code in ['BR1.1', user_data['user_cc']] else False
        if user_cc == 'BR1.1':
            context['user_can_change_status'] = True
        else:
            context['user_can_change_status'] = False

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
            context['formset_adm'] = AdmFormSet(instance=self.object)
            context['formset_unitlevel'] = UnitLevelFormSet(instance=self.object)

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
    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data.get('user_cc')
        # restrict create of new institution to BIREME (BR1.1)
        if user_cc != 'BR1.1':
            return HttpResponseForbidden()

        return super(InstCreateView, self).dispatch(*args, **kwargs)


class InstDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete objects
    """
    model = Institution
    success_url = reverse_lazy('list_institution')

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data.get('user_cc')
        # restrict delete of institution to BIREME (BR1.1)
        if user_cc != 'BR1.1':
            return HttpResponseForbidden()

        return super(InstCreateView, self).dispatch(*args, **kwargs)


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


@login_required
def add_unit(request):
    """
    Add Unit
    """
    success_url = ''
    if request.method == 'POST':
        form = UnitForm(request.POST)
        print form.errors
        if form.is_valid():
            new_unit = form.save()
            success_url = "{0}/?s={1}&country={2}".format(reverse_lazy('list_unit'),
                                                          new_unit.name, new_unit.country.id)
        else:
            param_country = request.POST.get('country')
            return render(request, 'institution/institution_unit.html',
                          {'form': form, 'param_country': param_country})

    return HttpResponseRedirect(success_url)

@login_required
def adhesionterm(request, institution_id):
    serviceproduct_list = ServiceProduct.objects.all()
    adhesionterm = AdhesionTerm.objects.last()
    inst_servproduct_list = []
    acepted_status = False

    if request.POST:
        acepted_param = request.POST.get('acepted_flag')
        set_list_param = request.POST.getlist('set')
        unset_list_param = request.POST.getlist('unset')

        acepted_flag = True if acepted_param == '1' else False

        inst_adhesion, created = InstitutionAdhesion.objects.get_or_create(
            institution_id=institution_id, adhesionterm_id=adhesionterm.pk
        )
        # update acepted flag
        inst_adhesion.acepted = acepted_flag
        inst_adhesion.save()

        if set_list_param or unset_list_param:
            # remove duplicated ID's from set/unset lists
            set_list = list(set(set_list_param))
            unset_list = list(set(unset_list_param))

            for srvprod_id in set_list:
                inst_servprod, created = InstitutionServiceProduct.objects.get_or_create(institution_id=institution_id,
                                                                            serviceproduct_id=srvprod_id)

            if unset_list:
                InstitutionServiceProduct.objects.filter(institution_id=institution_id, serviceproduct_id__in=unset_list).delete()


    else:
        # check if institution already acepted term
        inst_adhesion = InstitutionAdhesion.objects.filter(
                            institution=institution_id, adhesionterm=adhesionterm.pk)

        if inst_adhesion:
            acepted_status = inst_adhesion[0].acepted

        inst_servproduct_filter = InstitutionServiceProduct.objects.filter(institution_id=institution_id)
        inst_servproduct_list = [ips.serviceproduct for ips in inst_servproduct_filter]

        user_data = additional_user_info(request)
        user_cc = user_data['user_cc']

        # get log info for BR1.1 users (administrative)
        if user_cc ==  'BR1.1':
            if inst_adhesion:
                ctype_adhesion = ContentType.objects.get_for_model(inst_adhesion[0])
                logs_adhesion = LogEntry.objects.filter(content_type=ctype_adhesion,
                                                object_id=inst_adhesion[0].id)


            if inst_servproduct_filter:
                ctype_inst_servproduct = ContentType.objects.get_for_model(inst_servproduct_filter[0])

                inst_servproduct_id_list = [ips.id for ips in inst_servproduct_filter]
                logs_serviceproduct = LogEntry.objects.filter(content_type=ctype_inst_servproduct,
                                                    object_id__in=inst_servproduct_id_list)



    return render_to_response('institution/adhesionterm.html',
                              {'institution_id': institution_id, 'adhesionterm': adhesionterm,
                               'acepted_status': acepted_status, 'serviceproduct_list': serviceproduct_list,
                               'inst_servproduct_list': inst_servproduct_list},
                                context_instance=RequestContext(request))
