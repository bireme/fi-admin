#! coding: utf-8
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import F, Q

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType

from django.template import RequestContext

from django.db.models import Avg, Max, Min, Sum

from django.conf import settings

#from utils.views import ACTIONS
from utils.views import LoginRequiredView, SuperUserRequiredView, GenericUpdateWithOneFormset
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info

from title.models import *
from title.forms import *

# form actions
ACTIONS = {
    'orderby': 'id',
    'order': '-',
    'page': 1,
    'type': "",
    'issn': "",
    'id': "",
    's': "",
    'secs_number': "",
    'short_title': "",
    'filter_owner': "",
    'filter_status': "",
    'filter_thematic': "",
    'filter_created_by_user': "",
    'filter_created_by_cc': "",
}

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

        search_field = self.search_field + '__icontains'

        object_list = self.model.objects.filter(**{search_field: self.actions['s']})

        if self.actions['short_title'] != '':
            object_list = object_list.filter(shortened_title__icontains=self.actions['short_title'])

        if self.actions['id'] != '':
            object_list = object_list.filter(id_number=self.actions['id'])

        if self.actions['secs_number'] != '':
            object_list = object_list.filter(secs_number=self.actions['secs_number'])

        if self.actions['issn'] != '':
            object_list = object_list.filter(issn=self.actions['issn'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # if self.restrict_by_user and self.actions['filter_owner'] != "*":
        #     object_list = object_list.filter(created_by=self.request.user)
        # elif self.actions['filter_owner'] == "*":
        #     # restrict by cooperative center
        #     user_cc = self.request.user.profile.get_attribute('cc')
        #     object_list = object_list.filter(cooperative_center_code=user_cc)

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
        formset_issues = IssueFormSet(self.request.POST, instance=self.object)
        formset_links = OnlineResourcesFormSet(self.request.POST, instance=self.object)
        formset_specialty = BVSSpecialtyFormSet(self.request.POST, instance=self.object)
        formset_variance = TitleVarianceFormSet(self.request.POST, instance=self.object)
        formset_indexrange = IndexRangeFormSet(self.request.POST, instance=self.object)
        formset_audit = AuditFormSet(self.request.POST, instance=self.object)
        formset_collection = CollectionFormSet(self.request.POST, instance=self.object)
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_keyword = KeywordFormSet(self.request.POST, instance=self.object)
        formset_publicinfo = PublicInfoFormSet(self.request.POST, self.request.FILES, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_issues_valid = formset_issues.is_valid()
        formset_links_valid = formset_links.is_valid()
        formset_specialty_valid = formset_specialty.is_valid()
        formset_variance_valid = formset_variance.is_valid()
        formset_indexrange_valid = formset_indexrange.is_valid()
        formset_audit_valid = formset_audit.is_valid()
        formset_collection_valid = formset_collection.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_keyword_valid = formset_keyword.is_valid()
        formset_publicinfo_valid = formset_publicinfo.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(
            form,
            [
                formset_issues,
                formset_links,
                formset_specialty,
                formset_variance,
                formset_indexrange,
                formset_audit,
                formset_collection,
                formset_descriptor,
                formset_keyword,
            ]
        )

        if (form_valid and
            formset_issues_valid and
            formset_links_valid and
            formset_specialty_valid and
            formset_variance_valid and
            formset_indexrange_valid and
            formset_audit_valid and
            formset_collection_valid and
            formset_descriptor_valid and
            formset_keyword_valid and
            formset_publicinfo_valid and
            valid_for_publication):

            action = self.request.POST['action']

            # When previewing, editing or creating a title, if there is no file, the form is displayed again
            if action in ('preview', 'edit') and not self.request.FILES:
                view = 'title/form_preview.html' if action == 'preview' else 'title/title_form.html'

                return render(
                            self.request,
                            view,
                            self.get_context_data(
                                    form=form,
                                    formset_issues=formset_issues,
                                    formset_links=formset_links,
                                    formset_specialty=formset_specialty,
                                    formset_variance=formset_variance,
                                    formset_indexrange=formset_indexrange,
                                    formset_audit=formset_audit,
                                    formset_collection=formset_collection,
                                    formset_descriptor=formset_descriptor,
                                    formset_keyword=formset_keyword,
                                    formset_publicinfo=formset_publicinfo,
                                    valid_for_publication=valid_for_publication
                                    ))
            else:
                self.object = form.save()

                formset_issues.instance = self.object
                formset_issues.save()

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

                formset_collection.instance = self.object
                formset_collection.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_keyword.instance = self.object
                formset_keyword.save()

                formset_publicinfo.instance = self.object
                formset_publicinfo.save()

                # update models
                form.save()
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                            self.get_context_data(form=form,
                                formset_issues=formset_issues,
                                formset_links=formset_links,
                                formset_specialty=formset_specialty,
                                formset_variance=formset_variance,
                                formset_indexrange=formset_indexrange,
                                formset_audit=formset_audit,
                                formset_collection=formset_collection,
                                formset_descriptor=formset_descriptor,
                                formset_keyword=formset_keyword,
                                formset_publicinfo=formset_publicinfo,
                                valid_for_publication=valid_for_publication
                                ))


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
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        context['user_data'] = user_data
        context['role'] = user_role
        context['settings'] = settings

        if Title.objects.count() > 0:
            context['next_id'] = int(Title.objects.latest('id').id_number) + 1
        else:
            context['next_id'] = 1

        keep_context = True

        if self.request.method == 'GET':
            # special treatment for user of type documentalist is edit title from other user
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
                context['formset_collection'] = CollectionFormSet(instance=self.object)
                context['formset_publicinfo'] = PublicInfoFormSet(instance=self.object)
                # context['formset_issues'] = IssueFormSet(instance=self.object)

            else:
                context['formset_links'] = OnlineResourcesFormSet(instance=self.object)
                context['formset_specialty'] = BVSSpecialtyFormSet(instance=self.object)
                context['formset_variance'] = TitleVarianceFormSet(instance=self.object)
                context['formset_indexrange'] = IndexRangeFormSet(instance=self.object)
                context['formset_audit'] = AuditFormSet(instance=self.object)
                context['formset_collection'] = CollectionFormSet(instance=self.object)
                context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
                context['formset_keyword'] = KeywordFormSet(instance=self.object)
                context['formset_publicinfo'] = PublicInfoFormSet(instance=self.object)
                # context['formset_issues'] = IssueFormSet(instance=self.object)
        else:
            keep_context = False

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])
        context['actions'] = self.actions

        # Issues pagination
        if hasattr(self.object, 'id'):
            obj_id = self.object.id
        else:
            obj_id = None

        FormSet = IssueFormSet(instance=self.object)
        query = Issue.objects.all().filter(title=obj_id)

        user_cc = self.request.user.profile.get_attribute('cc')
        if self.actions['filter_owner'] != "" and user_cc == 'BR1.1':
            query = query.filter(cooperative_center_code=self.actions['filter_owner'])
        else:
            query = query.filter(cooperative_center_code=user_cc)

        paginator = Paginator(query, settings.ITEMS_PER_PAGE)
        page = self.request.GET.get('page')

        try:
            objects = paginator.page(page)
        except PageNotAnInteger:
            objects = paginator.page(1)
        except EmptyPage:
            objects = paginator.page(paginator.num_pages)

        page_query = query.filter(id__in=[object.id for object in objects])
        FormSet.queryset = page_query

        if objects.has_next():
            next_objects = paginator.page(objects.next_page_number())
            context['next_page_obj'] = next_objects[0]

        if objects.has_previous():
            prev_objects = paginator.page(objects.previous_page_number())
            context['prev_page_obj'] = prev_objects[-1]

        context['page_obj'] = objects
        context['filter_owner'] = user_cc if self.actions['filter_owner'] == "" else self.actions['filter_owner']
        context['cooperative_centers'] = Issue.objects.order_by('cooperative_center_code').values_list('cooperative_center_code', flat=True).distinct()

        if keep_context:
            context['formset_issues'] = FormSet

        return context


class TitleUpdateView(TitleUpdate, UpdateView):
    """
    Used as class view to update Title
    Extend TitleUpdate that do all the work
    """


class TitlePreview(TitleUpdate, UpdateView):
    """
    Used as class view to preview Title
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

        user_cc = self.request.user.profile.get_attribute('cc')
        if not user_cc == "BR1.1":
            raise Exception("Unauthorized")

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(TitleDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Keyword.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(TitleDeleteView, self).delete(request, *args, **kwargs)


def search_title(request):
    term = request.GET.get('term')
    filter_title_qs = Q(title__icontains=term) | Q(shortened_title__icontains=term)
    qs = Title.objects.filter(filter_title_qs).values_list("title", "shortened_title", "issn")

    # convert the result to a list with a dict containing the label and value attributes. Ex. [{"label": "Revista 1", "value": "Rev. 1|11111X"}]
    title_list = [{"label": title[0], "value": "%s|%s" % (title[1], title[2])} for title in qs]

    title_list_response = json.dumps(list(title_list), cls=DjangoJSONEncoder)


    return HttpResponse(title_list_response, content_type="application/json")


def get_indexcodes(request):
    title = request.GET.get('title')
    title_indexcodes = {}

    title_result = Title.objects.filter(shortened_title__iexact=title)
    if title_result:
        title_obj = title_result[0]
        index_range = IndexRange.objects.filter(title=title_obj.pk).annotate(index_db=F('index_code__name')).values("index_db")
        title_indexcodes = json.dumps(list(index_range), cls=DjangoJSONEncoder)


    return HttpResponse(title_indexcodes, content_type="application/json")