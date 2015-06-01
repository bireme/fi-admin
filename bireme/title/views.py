#! coding: utf-8
from django.core.urlresolvers import reverse, reverse_lazy

from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType

from django.conf import settings

from utils.views import ACTIONS
from utils.views import LoginRequiredView, SuperUserRequiredView, GenericUpdateWithOneFormset
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info

from models import *
from forms import *


class TitleCatalogView(LoginRequiredView, ListView):
    """
    Handle list view for Title objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    restrict_by_user = True
    
    def dispatch(self, *args, **kwargs):
        return super(TitleCatalogView, self).dispatch(*args, **kwargs)

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
        context = super(TitleCatalogView, self).get_context_data(**kwargs)
        context['actions'] = self.actions
        return context


# =================================== TITLE ==========================================

class TitleListView(TitleCatalogView, ListView):
    """
    Extend TitleCatalogView to list Serial objects
    """
    model = Title
    context_object_name = "titles"
    search_field = "title"

class TitleUpdate(LoginRequiredView):
    """
    Handle creation and update of Title objects
    """
    model = Title
    success_url = reverse_lazy('list_title')
    form_class = TitleForm
  
    def form_valid(self, form):
        formset_links = OnlineResourcesFormSet(self.request.POST, instance=self.object)
        formset_specialty = BVSSpecialtyFormSet(self.request.POST, instance=self.object)
        formset_variance = TitleVarianceFormSet(self.request.POST, instance=self.object)
        formset_indexrange = IndexRangeFormSet(self.request.POST, instance=self.object)
        formset_audit = AuditFormSet(self.request.POST, instance=self.object)
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_keyword = KeywordFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid() 

        formset_links_valid = formset_links.is_valid()
        formset_specialty_valid = formset_specialty.is_valid()
        formset_variance_valid = formset_variance.is_valid()
        formset_indexrange_valid = formset_indexrange.is_valid()
        formset_audit_valid = formset_audit.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_keyword_valid = formset_keyword.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(form, [formset_links, formset_specialty, formset_variance, formset_indexrange, formset_audit, formset_descriptor, formset_keyword])

        if (form_valid and formset_links_valid and formset_specialty_valid and formset_variance_valid and formset_indexrange_valid and formset_audit_valid and formset_descriptor_valid and formset_keyword_valid and valid_for_publication):
        
                self.object = form.save()

                formset_links.instance = self.object
                formset_links.save()

                formset_specialty.instance = self.object
                formset_specialty.save()

                formset_variance.instance = self.object
                formset_variance.save()

                formset_indexrange.instance = self.object
                formset_indexrange.save()

                formset_audit.instance = self.object
                formset_audit.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_keyword.instance = self.object
                formset_keyword.save()

                # update solr index
                form.save()
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                            self.get_context_data(form=form,
                                formset_links=formset_links,
                                formset_specialty=formset_specialty,
                                formset_variance=formset_variance,
                                formset_indexrange=formset_indexrange,
                                formset_audit=formset_audit,
                                formset_descriptor=formset_descriptor,
                                formset_keyword=formset_keyword,
                                valid_for_publication=valid_for_publication))

    
    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)


    def get_form_kwargs(self):
        kwargs = super(TitleUpdate, self).get_form_kwargs()
        user_data = additional_user_info(self.request)
        kwargs.update({'user': self.request.user, 'user_data': user_data})
        
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TitleUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('Title')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False
        
        context['user_data'] = user_data
        context['role'] = user_role
        context['settings'] = settings
        

        if self.request.method == 'GET':
            # special treatment for user of type documentalist is edit media from other user
            # add in the context list of descriptor already set for the title
            if user_role == 'doc' and self.object:
                c_type = ContentType.objects.get_for_model(self.get_object())

                context['descriptor_list'] = Descriptor.objects.filter(
                                                    object_id=self.object.id, 
                                                    content_type=c_type).exclude(
                                                    created_by_id=user_id, status=0)
                context['keyword_list'] = Keyword.objects.filter(
                                                    object_id=self.object.id,
                                                    content_type=c_type).exclude(
                                                    created_by_id=user_id, status=0)

                pending_descriptor_from_user = Descriptor.objects.filter(
                                                    created_by_id=self.request.user.id, status=0)
                pending_keyword_from_user = Keyword.objects.filter(
                                                    created_by_id=user_id, status=0)

                context['formset_descriptor'] = DescriptorFormSet(instance=self.object, 
                                                    queryset=pending_descriptor_from_user)
                context['formset_keyword']  = KeywordFormSet(instance=self.object,
                                                    queryset=pending_keyword_from_user)

                context['formset_links'] = OnlineResourcesFormSet(instance=self.object)
                context['formset_specialty'] = BVSSpecialtyFormSet(instance=self.object)
                context['formset_variance'] = TitleVarianceFormSet(instance=self.object)
                context['formset_indexrange'] = IndexRangeFormSet(instance=self.object)
                context['formset_audit'] = AuditFormSet(instance=self.object)
            else:
                context['formset_links'] = OnlineResourcesFormSet(instance=self.object)
                context['formset_specialty'] = BVSSpecialtyFormSet(instance=self.object)
                context['formset_variance'] = TitleVarianceFormSet(instance=self.object)
                context['formset_indexrange'] = IndexRangeFormSet(instance=self.object)
                context['formset_audit'] = AuditFormSet(instance=self.object)
                context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
                context['formset_keyword'] = KeywordFormSet(instance=self.object)

        return context


class TitleUpdateView(TitleUpdate, UpdateView):
    """
    Used as class view to update Title
    Extend TitleUpdate that do all the work    
    """


class TitleCreateView(TitleUpdate, CreateView):
    """
    Used as class view to create Title
    Extend TitleUpdate that do all the work
    """
   

class TitleDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of Title objects
    """
    model = Title
    success_url = reverse_lazy('list_title')

    def get_object(self, queryset=None):
        obj = super(TitleDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(TitleDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Keyword.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(TitleDeleteView, self).delete(request, *args, **kwargs)
