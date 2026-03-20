#! coding: utf-8
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

from django.shortcuts import render_to_response

from pkg_resources import resource_filename
from utils.views import get_class
from utils.forms import is_valid_for_publication
from utils.context_processors import additional_user_info
from attachments.models import Attachment
from main.models import Descriptor
from help.models import get_help_fields
from utils.views import LoginRequiredView, GenericUpdateWithOneFormset
from datetime import datetime

from oer.forms import *
from oer.search_indexes import *

import json
import colander
import deform


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
        for key in settings.ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, settings.ACTIONS[key])

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

        # filter by scope region country
        if self.actions['filter_country'] != '':
            object_list = object_list.filter(cvsp_node=self.actions['filter_country'])

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
        context = super(OERGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        show_advaced_filters = self.request.GET.get('apply_filters', False)
        user_role = user_data['service_role'].get('OER')
        cvsp_node_list = OER.objects.values_list('cvsp_node', flat=True).distinct()
        # remove empty values
        cvsp_node_list = filter(None, cvsp_node_list)

        context['actions'] = self.actions
        context['user_role'] = user_role
        context['cvsp_node_list'] = cvsp_node_list
        context['show_advaced_filters'] = show_advaced_filters

        return context


# ========================= Open Educational Resource ========================================================

class OERListView(OERGenericListView, ListView):
    """
    Extend OERGenericListView to list records
    """
    model = OER

class OERRelatedListView(ListView):
    """
    List resources (used by relationship popup selection window)
    """
    model = OER
    template_name = "oer/oer_related.html"
    paginate_by = 10
    context_object_name = "oer_list"

    def get_queryset(self):
        object_list = []

        param_search = self.request.GET.get('s')
        param_current = self.request.GET.get('current_oer')

        if param_search:
            object_list = self.model.objects.filter(title__icontains=param_search)
        else:
            object_list = self.model.objects.all()

        if param_current:
            object_list = object_list.exclude(id=param_current)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(OERRelatedListView, self).get_context_data(**kwargs)

        param_search = self.request.GET.get('s')
        param_current = self.request.GET.get('current_oer')

        context['param_search'] = param_search
        context['param_current'] = param_current

        return context


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
            formset_relation_valid and formset_attachment_valid):

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

                # update object
                form.save()
                # save many-to-many relation fields
                form.save_m2m()
                # update solr index
                update_search_index(self.object)

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
        kwargs = super(OERUpdate, self).get_form_kwargs()

        user_data = additional_user_info(self.request)
        kwargs.update({'user': self.request.user, 'user_data': user_data})

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(OERUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('OER')
        user_cc = user_data['user_cc']
        user_id = self.request.user.id
        user_cvsp_node = None
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

            # check if user participate of CVSP network
            user_network = user_data['networks']
            user_cvsp_node = next((node.lower() for node in user_network if node.startswith('CVSP')), None)
            if user_cvsp_node:
                user_cvsp_node = user_cvsp_node.split("-",1)[1]

        # create flag that control if user have permission to edit the reference
        obj = self.object
        if user_role == 'doc':
            # documentalist can create and edit your own records
            context['user_can_edit'] = True if not obj or ((obj.created_by == self.request.user) and obj.status < 1) else False
            context['user_can_change_status'] = False
        elif user_role == 'edi':
            # editor can create, edit and change status (publish) for oer of same center code or CVSP node
            context['user_can_edit'] = True if not obj or obj.cooperative_center_code == user_cc or obj.cvsp_node == user_cvsp_node else False
            context['user_can_change_status'] = True if not obj or obj.cooperative_center_code == user_cc or obj.cvsp_node == user_cvsp_node else False

        context['user_data'] = user_data
        context['user_role'] = user_role
        context['settings'] = settings
        context['help_fields'] = get_help_fields('oer')
        context['mandatory_fields'] = ['learning_objectives', 'description', 'type', 'learning_context',
                                       'language', 'creator', 'license']

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
            context['passive_relationship'] = Relationship.objects.filter(oer_referred=self.object)


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
        # check if cooperative center of the object is the same of the user
        user_cc = self.request.user.profile.get_attribute('cc')
        if not obj.cooperative_center_code == user_cc:
            return HttpResponse('Unauthorized', status=401)

        return obj

    def delete(self, request, *args, **kwargs):
        obj = super(OERDeleteView, self).get_object()
        c_type = ContentType.objects.get_for_model(obj)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ResourceThematic.objects.filter(object_id=obj.id, content_type=c_type).delete()

        # delete search index entry
        index = OERIndex()
        index.remove_object(obj)

        return super(OERDeleteView, self).delete(request, *args, **kwargs)

@csrf_exempt
def field_assist(request, **kwargs):

    # add search_path to override deform templates
    custom_deform_templates = '%s/templates/deform' % settings.BASE_DIR
    deform_templates = resource_filename('deform', 'templates')
    search_path = (custom_deform_templates, deform_templates)
    deform.Form.set_zpt_renderer(search_path)

    field_name = kwargs.get('field_name')
    # get previous value from field (json)
    field_value = request.POST.get('field_value', '')
    field_id = request.POST.get('field_id', field_name)

    formid = request.POST.get('__formid__', '')

    field_name_camelcase = field_name.title().replace('_', '')
    field_full_classname = 'oer.field_definitions.{0}'.format(field_name_camelcase)

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
        except ValidationFailure as e:
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


# update search index
def update_search_index(oer):
    if oer.status != -1:
        index = OERIndex()

        try:
            index.update_object(oer)
        except:
            pass