#! coding: utf-8
from django.core.urlresolvers import reverse, reverse_lazy

from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django.conf import settings

from utils.views import ACTIONS
from utils.views import LoginRequiredView, SuperUserRequiredView, GenericUpdateWithOneFormset
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info

from main.models import ThematicArea
from attachments.models import Attachment
from help.models import get_help_fields

from models import *
from forms import *


class MultimediaListView(LoginRequiredView, ListView):
    """
    Handle list view for multimedia objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    restrict_by_user = True

    def dispatch(self, *args, **kwargs):
        return super(MultimediaListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if ":" in self.actions["s"]:
            search_parts = self.actions["s"].split(":")
            search_field = search_parts[0] + "__icontains"
            search_value = search_parts[1]
        else:
            search_field = self.search_field + '__icontains'
            search_value = self.actions["s"]

        object_list = self.model.objects.filter(**{search_field: search_value})

        if self.actions['filter_status'] != '':
            object_list = object_list.filter(status=self.actions['filter_status'])

        if self.actions['filter_thematic'] != '':
            object_list = object_list.filter(thematics__thematic_area=int(self.actions['filter_thematic']))

        if self.actions['filter_created_by_user'] != '':
            object_list = object_list.filter(created_by_id=int(self.actions['filter_created_by_user']))

        if self.actions['filter_created_by_cc'] != '':
            object_list = object_list.filter(cooperative_center_code=self.actions['filter_created_by_cc'])

        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        if self.restrict_by_user and self.actions['filter_owner'] != "*":
            object_list = object_list.filter(created_by=self.request.user)

        elif self.actions['filter_owner'] == "*":
            object_list = object_list.all()

        return object_list

    def get_context_data(self, **kwargs):
        context = super(MultimediaListView, self).get_context_data(**kwargs)
        cc_filter_list = []
        user_filter_list = []

        user_data = additional_user_info(self.request)

        thematic_list = ThematicArea.objects.all().order_by('name')
        user_list = User.objects.filter(is_superuser=False).order_by('username')
        # mantain in user filter list only users from the same CCS (CC's in the network) as request.user
        '''
        for user in user_list:
            user_cc = user.profile.get_attribute('cc')
            if user_cc == user_data['user_cc'] or user_cc in user_data['ccs']:
                user_filter_list.append(user)
        '''
        cc_filter_list = user_data['ccs']
        # remove duplications from list
        cc_filter_list = list(set(cc_filter_list))
        cc_filter_list.sort()

        show_advaced_filters = self.request.GET.get('apply_filters', False)

        context['cc_filter_list'] = cc_filter_list
        context['user_filter_list'] = user_filter_list
        context['thematic_list'] = thematic_list
        context['show_advaced_filters'] = show_advaced_filters
        context['actions'] = self.actions
        return context


# ========================= MEDIA ========================================================

class MediaListView(MultimediaListView, ListView):
    """
    Extend MultimediaListView to list Media objects
    """
    model = Media
    context_object_name = "medias"
    search_field = "title"


class MediaUpdate(LoginRequiredView):
    """
    Handle creation and update of Media objects
    """
    model = Media
    success_url = reverse_lazy('list_media')
    form_class = MediaForm

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_keyword = KeywordFormSet(self.request.POST, instance=self.object)
        formset_thematic = ResourceThematicFormSet(self.request.POST, instance=self.object)
        formset_attachment = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_keyword_valid = formset_keyword.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_thematic_valid = formset_thematic.is_valid()
        formset_attachment_valid = formset_attachment.is_valid()

        # for status = admitted check  if the resource have at least one descriptor and one thematica area
        valid_for_publication = is_valid_for_publication(form,
                                                         [formset_descriptor, formset_keyword, formset_thematic])

        if (form_valid and formset_descriptor_valid and formset_keyword_valid and
           formset_thematic_valid and valid_for_publication and formset_attachment_valid):

                self.object = form.save()
                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_keyword.instance = self.object
                formset_keyword.save()

                formset_thematic.instance = self.object
                formset_thematic.save()

                formset_attachment.instance = self.object
                formset_attachment.save()

                # update solr index
                form.save()
                # save many-to-many relation fields
                form.save_m2m()
                return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_descriptor=formset_descriptor,
                                                 formset_keyword=formset_keyword,
                                                 formset_thematic=formset_thematic,
                                                 formset_attachment=formset_attachment,
                                                 valid_for_publication=valid_for_publication))

    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(MediaUpdate, self).get_form_kwargs()
        user_data = additional_user_info(self.request)
        kwargs.update({'user': self.request.user, 'user_data': user_data})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(MediaUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('Multimedia')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False
            c_type = ContentType.objects.get_for_model(self.get_object())
            context['c_type'] = c_type

        context['user_data'] = user_data
        context['role'] = user_role
        context['settings'] = settings
        context['help_fields'] = get_help_fields('multimedia')

        if self.request.method == 'GET':
            # special treatment for user of type documentalist is edit media from other user
            # add in the context list of descriptor, keyword and thematic already set for the media
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
                context['thematic_list'] = ResourceThematic.objects.filter(
                                                    object_id=self.object.id,
                                                    content_type=c_type).exclude(
                                                    created_by_id=user_id, status=0)

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

            context['formset_attachment'] = AttachmentFormSet(instance=self.object)

        return context


class MediaUpdateView(MediaUpdate, UpdateView):
    """
    Used as class view to update Media
    Extend MediaUpdate that do all the work
    """


class MediaCreateView(MediaUpdate, CreateView):
    """
    Used as class view to create Media
    Extend MediaUpdate that do all the work
    """


class MediaDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of Media objects
    """
    model = Media
    success_url = reverse_lazy('list_media')

    def get_object(self, queryset=None):
        obj = super(MediaDeleteView, self).get_object()
        """ Hook to ensure object is owned by request.user. """
        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(MediaDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Keyword.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()

        return super(MediaDeleteView, self).delete(request, *args, **kwargs)


# ========================= MEDIA TYPE ===================================================
class MediaTypeListView(MultimediaListView, SuperUserRequiredView, ListView):
    """
    Extend MultimediaListView to list MediaType objects
    """
    model = MediaType
    context_object_name = "types"
    search_field = "name"
    restrict_by_user = False


class MediaTypeUpdate(SuperUserRequiredView, GenericUpdateWithOneFormset):
    """
    Handle creation and update of MediaType objects
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = MediaType
    success_url = reverse_lazy('list_mediatypes')
    formset = TypeTranslationFormSet
    fields = '__all__'


class MediaTypeUpdateView(MediaTypeUpdate, UpdateView):
    """
    Used as class view for update media type
    Extend MediaTypeUpdate that do all the work
    """


class MediaTypeCreateView(MediaTypeUpdate, CreateView):
    """
    Used as class view for create media type
    Extend MediaTypeUpdate that do all the work
    """


class MediaTypeDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of MediaType objects
    """
    model = MediaType
    success_url = reverse_lazy('list_mediatypes')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(MediaTypeDeleteView, self).get_object()

        if not self.request.user.is_superuser or not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj


# ========================= MEDIA COLLECTION =============================================
class MediaCollectionListView(MultimediaListView, ListView):
    """
    Extend MultimediaListView to list Media Collection objects
    """
    model = MediaCollection
    context_object_name = "collections"
    search_field = "name"
    restrict_by_user = False


class MediaCollectionUpdate(GenericUpdateWithOneFormset):
    """
    Handle create/edit of Media Collection
    Use GenericUpdateWithOneFormset to render form and formset
    """
    model = MediaCollection
    form_class = MediaCollectionForm
    success_url = reverse_lazy('list_mediacollections')
    formset = MediaCollectionTranslationFormSet


class MediaCollectionCreateView(MediaCollectionUpdate, CreateView):
    """
    Used as class view for create media collection
    Extend MediaCollectionUpdate that do all the work
    """


class MediaCollectionEditView(MediaCollectionUpdate, UpdateView):
    """
    Used as class view for edit media type
    Extend MediaCollectionUpdate that do all the work
    """


class MediaCollectionDeleteView(LoginRequiredView, DeleteView):
    """
    Handle delete of MediaType collection objects
    """
    model = MediaCollection
    success_url = reverse_lazy('list_mediacollections')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(MediaCollectionDeleteView, self).get_object()

        if not obj.created_by == self.request.user:
            return HttpResponse('Unauthorized', status=401)
        return obj
