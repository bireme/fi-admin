#! coding: utf-8
from collections import defaultdict
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.functions import Substr

from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

from field_definitions import FIELDS_BY_DOCUMENT_TYPE

from utils.views import ACTIONS
from cross_validation import check_for_publication
from utils.context_processors import additional_user_info
from attachments.models import Attachment
from main.models import Descriptor
from title.models import Title
from database.models import Database
from classification.models import Collection
from help.models import get_help_fields
from utils.views import LoginRequiredView
from forms import *

import json
import requests

JOURNALS_FASCICLE = "S"


class BiblioRefGenericListView(LoginRequiredView, ListView):
    """
    Handle list view for bibliographic records objects
    """
    paginate_by = settings.ITEMS_PER_PAGE
    context_object_name = "references"
    search_field = "reference_title"

    def dispatch(self, *args, **kwargs):
        self.request.session["filtered_list"] = self.request.get_full_path()
        return super(BiblioRefGenericListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        source_id = self.request.GET.get('source', None)
        document_type = self.request.GET.get('document_type', None)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')
        # identify view and model in use
        view_name = self.view_name
        model_name = self.model.__name__

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if settings.FULLTEXT_SEARCH:
            search_field = self.search_field + '__search'
        else:
            search_field = self.search_field + '__icontains'


        # check if user has perform a search
        search = self.actions['s']
        if search:
            if ':' in search:
                search_parts = search.split(':')
                lookup_expr = '__exact' if search_parts[0] == "LILACS_original_id" else '__icontains'
                search_field, search = "%s%s" % (search_parts[0], lookup_expr), search_parts[1]
            elif settings.FULLTEXT_SEARCH:
                # check if user is searching by serial. Ex. Mem. Inst. Oswaldo Cruz; 14 (41)
                exp_serial = re.compile('[\.\;\(\)\|]')
                if bool(re.search(exp_serial, search)):
                    # search using quotes
                    search = u'"{}"'.format(search)
                else:
                    # search using boolean AND
                    search = u"+{}".format(search.replace(' ', ' +'))

            object_list = self.model.objects.filter(**{search_field: search})
        else:
            # check if user are list analytics from source
            if source_id:
                object_list = self.model.objects.filter(source_id=source_id)
            else:
                object_list = self.model.objects.all()


        # get user filter values
        filter_status = self.actions.get('filter_status')
        filter_indexed_database = self.actions.get('filter_indexed_database')
        filter_collection = self.actions.get('filter_collection')
        filter_owner = self.actions.get('filter_owner')
        filter_network = self.actions.get('filter_network')

        # default value for filter status (ALL)
        if filter_status == '':
            filter_status = '*'

        if filter_indexed_database != '':
            object_list = object_list.filter(indexed_database=filter_indexed_database)

        if filter_collection != '':
            object_list = object_list.filter(collection__collection_id=filter_collection)


        # filter by specific document type and remove filter by user (filter_owner)
        if document_type:
            literature_type = re.sub('[^A-Z]|[CP]', '', document_type)  # get only uppercase chars excepct CP (congress/project)
            treatment_level = re.sub('[A-Z]', '', document_type)  # get only lowercase chars
            object_list = object_list.filter(literature_type__startswith=literature_type,
                                             treatment_level=treatment_level)

        # apply custom order if user filter by journals fascicle in reference list
        if document_type == JOURNALS_FASCICLE:
            object_list = object_list.annotate(
                publication_year=Substr("publication_date_normalized", 1, 4)
            )

            if model_name == "Reference":
                volume_serial_field = "referencesource__volume_serial"
                issue_number_field = "referencesource__issue_number"
            else:
                volume_serial_field = "volume_serial"
                issue_number_field = "issue_number"

            object_list = object_list.order_by(
                "-publication_year",
                "-{}".format(volume_serial_field),
                "-{}".format(issue_number_field)
            )
        elif self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # if not at main reference list and source or document_type remove filter by user
        if model_name != 'Reference' and (source_id or document_type):
            filter_owner = '*'

        # profile lilacs express editor - restrict by CC code when list sources
        if document_type and user_role == 'editor_llxp':
            filter_owner = 'center'

        # filter by user
        if not filter_owner or filter_owner == 'user':
            object_list = object_list.filter(created_by=self.request.user)
        # filter by cooperative center
        elif filter_owner == 'center':
            user_cc = self.request.user.profile.get_attribute('cc')
            object_list = object_list.filter(cooperative_center_code=user_cc)
        # filter by titles of responsibility of current user CC
        elif filter_owner == 'indexed' or (view_name == 'list_biblioref_sources' and document_type == 'S'):
            user_cc = self.request.user.profile.get_attribute('cc')
            titles_indexed = [t.shortened_title for t in Title.objects.filter(indexrange__indexer_cc_code=user_cc)]
            if titles_indexed:
                # by default filter by LILACS express status (status = 0)
                if filter_owner == 'indexed' and self.actions.get('filter_status') == '':
                    filter_status = 0

                # by default filter by articles (exclude sources of list)
                if not document_type:
                    object_list = object_list.filter(literature_type__startswith='S', treatment_level='as')

                # filter by serial list indexed by center
                filter_title_qs = Q()
                for title in titles_indexed:
                        if not document_type or document_type == 'Sas':
                            filter_title_qs = filter_title_qs | Q(referenceanalytic__source__title_serial=title)
                        else:
                            if model_name == 'Reference':
                                filter_title_qs = filter_title_qs | Q(referencesource__title_serial=title)
                            else:
                                filter_title_qs = filter_title_qs | Q(title_serial=title)

                object_list = object_list.filter(filter_title_qs)

            else:
                # if no indexed journals are found return a empty list
                object_list = self.model.objects.none()

        # filter by records changed by others
        elif filter_owner == 'review':
            if self.actions['review_type'] == 'user':
                ref_list = refs_changed_by_other_user(self.request.user)
            else:
                ref_list = refs_changed_by_other_cc(self.request.user)

            if ref_list:
                # get only ID's from filter reference list
                reference_id_list = ref_list.keys
                object_list = object_list.filter(id__in=reference_id_list)
            else:
                object_list = object_list.none()


        # default filter_network for AIM
        if filter_owner == '*' and not filter_network and 'AIM' in user_data['networks']:
            filter_network = 'AIM'

        # apply filter network
        if filter_network and filter_network != '*':
            if 'ccs_by_network' in user_data:
                ccs_in_network = user_data['ccs_by_network'].get(filter_network, [])
                object_list = object_list.filter(cooperative_center_code__in=ccs_in_network)


        # apply filter status
        if filter_status != '*':
            object_list = object_list.filter(status=filter_status)

        return object_list

    def get_context_data(self, **kwargs):
        context = super(BiblioRefGenericListView, self).get_context_data(**kwargs)
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')
        source_id = self.request.GET.get('source')

        # change defaults filter for indexed tab
        if self.actions['filter_owner'] == 'indexed':
            filter_status = self.actions.get('filter_status')
            self.actions['document_type'] = self.actions.get('document_type') or 'Sas'
            if filter_status == '':
                self.actions['filter_status'] = '0'

        # set default filter for users in AIM network
        if self.actions['filter_owner'] == '*' and not self.actions['filter_network'] and 'AIM' in user_data['networks']:
            self.actions['filter_network'] = 'AIM'

        context['actions'] = self.actions
        context['document_type'] = self.request.GET.get('document_type')
        context['source_id'] = self.request.GET.get('source')
        context['user_role'] = user_role
        context['indexed_database_list'] = Database.objects.all().order_by('name')
        context['collection_list'] = Collection.objects.all().order_by('parent_id')

        if source_id:
            context['reference_source'] = ReferenceSource.objects.get(pk=source_id)

        return context


# ========================= BiblioRef ========================================================

class BiblioRefListView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic records
    """
    model = Reference
    view_name = 'list_biblioref'


class BiblioRefListSourceView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic records
    """
    model = ReferenceSource
    view_name = 'list_biblioref_sources'


class BiblioRefListAnalyticView(BiblioRefGenericListView, ListView):
    """
    Extend BiblioRefGenericListView to list bibliographic records
    """
    model = ReferenceAnalytic
    view_name = 'list_biblioref_analytics'


class BiblioRefUpdate(LoginRequiredView):
    """
    Handle creation and update of bibliographic records
    """

    success_url = reverse_lazy('list_biblioref')

    def form_valid(self, form):
        formset_descriptor = DescriptorFormSet(self.request.POST, instance=self.object)
        formset_attachment = AttachmentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        formset_library = LibraryFormSet(self.request.POST, instance=self.object)
        formset_complement = ComplementFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()

        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_attachment_valid = formset_attachment.is_valid()
        formset_library_valid = formset_library.is_valid()
        formset_complement_valid = formset_complement.is_valid()

        user_data = additional_user_info(self.request)
        # run cross formsets validations
        valid_for_publication = check_for_publication(form, {'descriptor': formset_descriptor,
                                                             'attachment': formset_attachment}, user_data)

        if (form_valid and formset_descriptor_valid and formset_attachment_valid and
           formset_complement_valid and valid_for_publication):

                self.object = form.save()

                # Check if is present conference or project complement
                complement_conference = formset_complement.cleaned_data[0].get('conference_name')
                complement_project = (formset_complement.cleaned_data[0].get('project_name') or
                                      formset_complement.cleaned_data[0].get('project_number'))

                # Update information at literature_type field
                if complement_conference:
                    self.object.literature_type += 'C'
                elif 'C' in self.object.literature_type:
                    self.object.literature_type = self.object.literature_type.replace('C', '')

                if complement_project:
                    self.object.literature_type += 'P'
                elif 'P' in self.object.literature_type:
                    self.object.literature_type = self.object.literature_type.replace('P', '')

                if (complement_conference or complement_project):
                    self.object.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_attachment.instance = self.object
                formset_attachment.save()

                formset_library.instance = self.object
                formset_library.save()

                formset_complement.instance = self.object
                formset_complement.save()

                # save many-to-many relation fields
                form.save_m2m()
                # update solr index
                form.save()
                # update DeDup service
                update_dedup_service(self.object)

                # if record is a serial source update analytics auxiliary field reference_title
                if self.object.literature_type == 'S' and not hasattr(self.object, 'source'):
                    update_reference_tite(self.object)


                return HttpResponseRedirect(self.get_success_url())
        else:
            # if not valid for publication return status to original (previous) value
            if self.object:
                previous_status = self.object.previous_value('status')
                self.object.status = previous_status
                form.data['status'] = previous_status
            else:
                form.data['status'] = '-1'

            return self.render_to_response(
                           self.get_context_data(form=form,
                                                 formset_descriptor=formset_descriptor,
                                                 formset_attachment=formset_attachment,
                                                 formset_library=formset_library,
                                                 formset_complement=formset_complement,
                                                 valid_for_publication=valid_for_publication))

    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(BiblioRefUpdate, self).get_form_kwargs()
        document_type = ''
        reference_source = None

        source_id = self.request.GET.get('source', None)
        # new analytic
        if source_id:
            reference_source = ReferenceSource.objects.get(pk=source_id)
            literature_type = reference_source.literature_type
            treatment_level = reference_source.treatment_level
            # remove congress/project from literature_type
            literature_type = re.sub('[CP]', '', literature_type)

            if literature_type == 'S':
                document_type = 'Sas'
            else:
                if 'c' in treatment_level:
                    document_type = "{0}amc".format(literature_type)
                elif 's' in treatment_level:
                    document_type = "{0}ams".format(literature_type)
                else:
                    document_type = "{0}am".format(literature_type)

        # edition/new source
        else:
            # source/analytic edition
            if self.object:
                if hasattr(self.object, 'source'):
                    reference_source = self.object.source

                # remove congress/project from literature_type
                literature_type = re.sub('[CP]', '', self.object.literature_type)

                document_type = "{0}{1}".format(literature_type, self.object.treatment_level)
            # new source
            else:
                document_type = self.request.GET.get('document_type')


        # get list of fields allowed by document_type
        fieldsets = FIELDS_BY_DOCUMENT_TYPE.get(document_type, None)

        user_data = additional_user_info(self.request)

        additional_form_parameters = {}
        additional_form_parameters['user'] = self.request.user
        additional_form_parameters['user_data'] = user_data
        additional_form_parameters['fieldsets'] = fieldsets
        additional_form_parameters['document_type'] = document_type
        additional_form_parameters['reference_source'] = reference_source

        kwargs.update(additional_form_parameters)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(BiblioRefUpdate, self).get_context_data(**kwargs)

        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')
        user_id = self.request.user.id
        if self.object:
            user_data['is_owner'] = True if self.object.created_by == self.request.user else False

        context['user_data'] = user_data
        context['user_role'] = user_role

        # create flag that control if user have permission to edit the reference
        if user_role == 'editor_llxp':
            context['user_can_edit'] = True if not self.object or (self.object.status != 1 and self.object.cooperative_center_code == user_data['user_cc']) else False
            context['user_can_change_status'] = False
        elif user_role == 'doc':
            context['user_can_edit'] = True if not self.object or self.object.status < 1 or (self.object.status != 1 and self.object.cooperative_center_code == user_data['user_cc']) else False
            context['user_can_change_status'] = False
        else:
            context['user_can_edit'] = True
            context['user_can_change_status'] = True

        view_mode = self.request.GET.get('view_mode', False)
        if view_mode:
            context['user_can_edit'] = False

        context['settings'] = settings
        context['view_mode'] = view_mode
        context['help_fields'] = get_help_fields('biblioref')

        if self.object:
            # pass contenttype of object (analytic or source) and parent (reference)
            context['c_type'] = ContentType.objects.get_for_model(self.get_object())
            context['c_type_parent'] = ContentType.objects.get_for_model(Reference)

        if self.request.method == 'GET':
            context['formset_descriptor'] = DescriptorFormSet(instance=self.object)
            context['formset_attachment'] = AttachmentFormSet(instance=self.object)
            context['formset_library'] = LibraryFormSet(instance=self.object,
                                                        queryset=ReferenceLocal.objects.filter(cooperative_center_code=user_data['user_cc']))
            context['formset_complement'] = ComplementFormSet(instance=self.object)

        # source/analytic edition
        if self.object:
            context['document_type'] = "{0}{1}".format(self.object.literature_type, self.object.treatment_level)
        # new source
        else:
            document_type = self.request.GET.get('document_type')
            source_id = self.request.GET.get('source')

            if document_type:
                context['document_type'] = document_type
            elif source_id:
                reference_source = ReferenceSource.objects.get(pk=source_id)
                literature_type = reference_source.literature_type
                if literature_type == 'S':
                    document_type = 'Sas'
                else:
                    document_type = "{0}am".format(literature_type)

                context['document_type'] = document_type


        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        user_data = additional_user_info(self.request)
        user_role = user_data['service_role'].get('LILDBI')

        if user_role == 'editor_llxp':
            redirect_url = "%s?document_type=S" % reverse_lazy('list_biblioref_sources')
        else:
            redirect_url = self.request.session.get("filtered_list", self.success_url)

        return redirect_url


class BiblioRefSourceUpdateView(BiblioRefUpdate, UpdateView):
    """
    Used as class view to update BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceSource
    form_class = BiblioRefSourceForm


class BiblioRefAnaliticUpdateView(BiblioRefUpdate, UpdateView):
    """
    Used as class view to update BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceAnalytic
    form_class = BiblioRefAnalyticForm

    def get_context_data(self, **kwargs):
        # add source to context of form to present source information
        context = super(BiblioRefAnaliticUpdateView, self).get_context_data(**kwargs)
        context['reference_source'] = self.object.source

        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        success_url = self.request.session.get(
            'filtered_list',
            '/bibliographic/analytics?source=%s' % self.object.source.id
        )
        return success_url


class BiblioRefSourceCreateView(BiblioRefUpdate, CreateView):
    """
    Used as class view to create BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceSource
    form_class = BiblioRefSourceForm

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        redirect_url = ''
        if self.object.literature_type[0] == 'S':
            redirect_url = 'new-analytic?source=%s' % self.object.pk
        else:
            redirect_url = '/bibliographic/'

        return redirect_url


class BiblioRefAnalyticCreateView(BiblioRefUpdate, CreateView):
    """
    Used as class view to create BiblioRef
    Extend BiblioRefUpdate that do all the work
    """
    model = ReferenceAnalytic
    form_class = BiblioRefAnalyticForm

    def get_context_data(self, **kwargs):
        # add source to context of form to present source information
        context = super(BiblioRefAnalyticCreateView, self).get_context_data(**kwargs)
        source_id = self.request.GET.get('source', None)

        if source_id:
            reference_source = ReferenceSource.objects.get(pk=source_id)
            context['reference_source'] = reference_source

        return context

    # after creation of source present option for creation new analytic
    def get_success_url(self):
        source_id = self.request.GET.get('source', None)
        return 'analytics?source=%s' % source_id


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
        child_class = obj.child_class()
        c_type = ContentType.objects.get_for_model(child_class)

        # delete associated data
        Descriptor.objects.filter(object_id=obj.id, content_type=c_type).delete()
        Attachment.objects.filter(object_id=obj.id, content_type=c_type).delete()
        ReferenceLocal.objects.filter(source=obj.id).delete()
        ReferenceComplement.objects.filter(source=obj.id).delete()

        return super(BiblioRefDeleteView, self).delete(request, *args, **kwargs)


@csrf_exempt
def view_duplicates(request, reference_id):
    """
    Present list of duplicates references (identified at migration process)
    """
    duplicate_list = ReferenceDuplicate.objects.filter(reference=reference_id)
    metadata = indexing = library = complement = other = {}
    duplicate = None

    duplicate_id = request.GET.get('duplicate_id')
    if duplicate_id:
        duplicate = ReferenceDuplicate.objects.get(pk=duplicate_id)
    elif duplicate_list.count() == 1:
        duplicate = duplicate_list[0]

    if duplicate:
        try:
            metadata = json.loads(duplicate.metadata_json)
            indexing = json.loads(duplicate.indexing_json)
            library = json.loads(duplicate.library_json)
            complement = json.loads(duplicate.complement_json)
            other = json.loads(duplicate.others_json)
        except:
            # ignore possible errors at json load at field (eg. empty field)
            pass

    return render_to_response('biblioref/duplicate_detail.html', {'duplicate_list': duplicate_list,
                                                                  'duplicate': duplicate,
                                                                  'metadata': metadata,
                                                                  'indexing': indexing,
                                                                  'library': library,
                                                                  'complement': complement,
                                                                  'other': other,
                                                                  })


def refs_changed_by_other_cc(current_user):
    """
    Return dictionary with id of reference and log object changed by other cooperative centers
    """
    current_user_cc = current_user.profile.get_attribute('cc')
    result_list = defaultdict(list)

    # get last references of current user cooperative center
    refs_from_cc = Reference.objects.filter(cooperative_center_code=current_user_cc).order_by('-id')[:100]

    for reference in refs_from_cc:
        # get correct class (source our analytic)
        c_type = reference.get_content_type_id
        # filter by logs of current reference, change type and made by other users
        log_list = LogEntry.objects.filter(object_id=reference.id, content_type=c_type, action_flag=2) \
                                   .exclude(user=current_user).order_by('-id')

        if log_list:
            # exclude from list all changes that was already reviewed (logreview is created)
            log_list = log_list.exclude(logreview__isnull=False)

        # create list of log users of same cc
        exclude_user_list = []
        for log in log_list:
            log_user_cc = log.user.profile.get_attribute('cc')
            if log_user_cc == current_user_cc:
                exclude_user_list.append(log.user)
        # exclude from log list users from same cc as current user
        if exclude_user_list:
            log_list = log_list.exclude(user__in=exclude_user_list)

        if log_list:
            # group result by id (one line for each reference)
            for log in log_list:
                result_list[log.object_id] = log

    return result_list


def refs_changed_by_other_user(current_user):
    """
    Return dictionary with id of reference and log object changed by other user
    """
    log_list = []
    result_list = defaultdict(list)

    # get references created by current user
    refs_from_user = Reference.objects.filter(created_by=current_user)
    for reference in refs_from_user:
        # get correct class (source our analytic)
        c_type = reference.get_content_type_id
        # filter by logs of current reference, change type and made by other users
        changed_by_other_user = LogEntry.objects.filter(object_id=reference.id, content_type=c_type, action_flag=2) \
                                                .exclude(user=current_user).order_by('-id')
        if changed_by_other_user:
            # exclude from list all changes that was already reviewed (logreview is created)
            changed_by_other_user = changed_by_other_user.exclude(logreview__isnull=False)

        log_list.extend(changed_by_other_user)

    # group result (one line for each reference)
    if log_list:
        # group result by id (one line for each reference)
        for log in log_list:
            result_list[log.object_id] = log


    return result_list


def refs_llxp_for_indexing(current_user):

    user_cc = current_user.profile.get_attribute('cc')

    # first filter by LLXP records
    ref_list = Reference.objects.filter(status=0)

    titles_indexed = [t.shortened_title for t in Title.objects.filter(indexrange__indexer_cc_code=user_cc)]
    filter_title_qs = Q()
    for title in titles_indexed:
        filter_title_qs = filter_title_qs | Q(referenceanalytic__source__title_serial=title)

    # filter by titles indexed by current user cc
    ref_list = ref_list.filter(filter_title_qs)

    return ref_list


# update DeDup service
def update_dedup_service(obj):
    if obj.document_type() == 'Sas':
        # send multiple DeDup entries with the same ID for each title #728
        for article_title in obj.title:
            # for status LLXP and Published use more complete schema of DeDup index
            if obj.status == 0 or obj.status == 1:
                dedup_schema = 'LILACS_Sas_Seven'
                author_list = [au.get('text') for au in obj.individual_author] if obj.individual_author else []
                first_page = obj.pages[0].get('_f', '') if obj.pages else ''
                dedup_params = {"ano_publicacao": obj.source.publication_date_normalized[:4],
                                "numero_fasciculo": obj.source.issue_number, "volume_fasciculo": obj.source.volume_serial,
                                "titulo_artigo": article_title['text'], "titulo_revista": obj.source.title_serial,
                                "autores": '//@//'.join(author_list), "pagina_inicial": first_page}
            else:
                dedup_schema = 'LILACS_Sas_Five'
                dedup_params = {"ano_publicacao": obj.source.publication_date_normalized[:4],
                                "numero_fasciculo": obj.source.issue_number, "volume_fasciculo": obj.source.volume_serial,
                                "titulo_artigo": article_title['text'], "titulo_revista": obj.source.title_serial}

            json_data = json.dumps(dedup_params, ensure_ascii=True)
            dedup_headers = {'Content-Type': 'application/json'}
            # send to DeDup FIADMIN ID with title language code. Ex. fiadmin-99999-pt #728
            ref_id = "fiadmin-{0}-{1}".format(obj.id, article_title['_i'])

            dedup_url = "{0}/{1}/{2}/{3}".format(settings.DEDUP_PUT_URL, 'lilacs_Sas', dedup_schema, ref_id)
            try:
                dedup_request = requests.post(dedup_url, headers=dedup_headers, data=json_data, timeout=5)
            except:
                pass

    elif obj.document_type() == 'S':
            dedup_schema = 'LILACS_Sas_Source'
            dedup_params = {"data_iso": obj.publication_date_normalized[:4], "ISSN": obj.issn,
                            "numero_fasciculo": obj.issue_number, "volume_fasciculo": obj.volume_serial,
                            "titulo_revista": obj.title_serial}

            json_data = json.dumps(dedup_params, ensure_ascii=True)
            dedup_headers = {'Content-Type': 'application/json'}
            ref_id = "fiadmin-{0}".format(obj.id)

            dedup_url = "{0}/{1}/{2}/{3}".format(settings.DEDUP_PUT_URL, 'lilacs_Sas_Source', dedup_schema, ref_id)

            try:
                dedup_request = requests.post(dedup_url, headers=dedup_headers, data=json_data, timeout=5)
            except:
                pass



# update auxiliary field reference_title
def update_reference_tite(source):
    analytic_list = ReferenceAnalytic.objects.filter(source=source.id)
    for analytic in analytic_list:
        # try update field on each analytic record
        try:
            analytic_title = analytic.title[0]['text']
            analytic.reference_title = u"{0} | {1}".format(source.reference_title, analytic_title)
            # update only specific fields to avoid mess up json fields (escape)
            analytic.save(update_fields=['reference_title', 'updated_time', 'updated_by'])
        except:
            pass
