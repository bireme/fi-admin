#! coding: utf-8

from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView

from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.contenttypes.models import ContentType

from django.views import generic

from utils.views import LoginRequiredView, GenericUpdateWithOneFormset

from django.conf import settings

from models import *
from forms import *

from django.db.models import Prefetch
from django.db.models import Q

from django.utils.translation import ugettext_lazy as _, get_language
from django.core.paginator import Paginator


from django.contrib import messages

import datetime


from utils.context_processors import additional_user_info


ITEMS_PER_PAGE = 10

# form actions
ACTIONS = {
    'term_string': '',
    'filter_language': '',
    'descriptor_ui': '',

    'abbreviation': '',
    'qualifier_ui': '',

    'filter_fields': '',
    'filter_status': '',

    'decs_code': '',
    'tree_number': '',
    'concept_ui': '',

    'orderby': 'id',
    'order': '',
    'page': 1,

    'visited': '',
    's': '',
    'exact': '',

    'form_language': '',

    'choiced_thesaurus': '',
    'choiced_thesaurus_name': '',
    'choiced_concept_identifier_id': '',
    'choiced_term_id': '',
    'choiced_term_string': '',
    'choiced_language_code': '',
}



# Descriptors ------------------------------------------------------------------------
class DescUpdate(LoginRequiredView):
    """
    Handle creation and update of Descriptors objects
    Create the first form
    """
    model = IdentifierDesc
    success_url = reverse_lazy('create_concept_termdesc')
    
    form_class = IdentifierDescForm
    template_name = "thesaurus/descriptor_form_step1.html"

    def form_valid(self, form):
        formset_descriptor = DescriptionDescFormSet(self.request.POST, instance=self.object)
        formset_treenumber = TreeNumbersListDescFormSet(self.request.POST, instance=self.object)
        formset_pharmaco = PharmacologicalActionListDescFormSet(self.request.POST, instance=self.object)
        formset_related = SeeRelatedListDescFormSet(self.request.POST, instance=self.object)
        formset_previous = PreviousIndexingListDescFormSet(self.request.POST, instance=self.object)
        formset_entrycombination = EntryCombinationListDescFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_treenumber_valid = formset_treenumber.is_valid()
        formset_pharmaco_valid = formset_pharmaco.is_valid()
        formset_related_valid = formset_related.is_valid()
        formset_previous_valid = formset_previous.is_valid()
        formset_entrycombination_valid = formset_entrycombination.is_valid()

        if (form_valid and 
            formset_descriptor_valid and 
            formset_treenumber_valid and 
            formset_pharmaco_valid and
            formset_related_valid and
            formset_previous_valid and
            formset_entrycombination_valid
            ):

            # Verifica se foi passado algum valor para formset_treenumber
            tree_number_existentes=''
            exist_tree_numbers=0
            for f in formset_treenumber:
                if f.cleaned_data is not None:
                    fields_t = f.cleaned_data
                    content_tree_number = fields_t.get('tree_number')

                    # Essa variável é do cleaned_data e diz se o registro foi apagado ou não no formulário
                    # Se for True foi apagado
                    status_preenchimento = fields_t.get('DELETE')

                    if status_preenchimento == False:
                        exist_tree_numbers = exist_tree_numbers + 1

                        # Verifica se ja existe cadastrado o tree_number para este tesauro
                        result_tree_number = TreeNumbersListDesc.objects.filter(tree_number=content_tree_number).values('identifier_id')

                        if result_tree_number is not None:
                            for t in result_tree_number:
                                identifier_id_existent_tree_number = t.get('identifier_id')

                                # Checks if the record is for the thesaurus being worked on
                                res_existent_thesaurus_id = IdentifierDesc.objects.filter(id=identifier_id_existent_tree_number).values('thesaurus_id')
                                existent_thesaurus_id=res_existent_thesaurus_id[0].get('thesaurus_id')

                                # Brings id of thesaurus currently operating
                                environment_thesaurus_id = self.request.GET.get("ths")

                                # If tree_number exists in same thesaurus creates error
                                if int(environment_thesaurus_id) == int(existent_thesaurus_id):
                                    tree_number_existentes = tree_number_existentes + content_tree_number + '   '

            # Condição para poder criar registro
            if not tree_number_existentes and exist_tree_numbers > 0:

                # Bring the choiced language_code from the first form
                registry_language = self.request.GET.get("language_code")

                # Get sequential number to write to decs_code
                self.object = form.save(commit=False)
                ths = self.request.GET.get("ths")
                try:
                    seq = code_controller.objects.get(thesaurus=self.request.GET.get("ths"))
                    nseq = str(int(seq.sequential_number) + 1)
                    seq.sequential_number = nseq
                    seq.save()
                except code_controller.DoesNotExist:
                    seq = code_controller(sequential_number=1,thesaurus=ths)
                    nseq = 1
                    seq.save()
                self.object.decs_code = nseq
                self.object = form.save(commit=True)

                # Get thesaurus_acronym to create new ID format to descriptor_ui field
                self.object = form.save(commit=False)
                try:
                    acronym = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_acronym')
                    # recupera o acronimo e transforma em maiusuclo
                    acronym = str(acronym[0].get('thesaurus_acronym')).upper()
                    # utiliza self.object.decs_code para compor descriptor_ui
                    zseq = str(self.object.decs_code).zfill(6) # preenche zeros a esquerda
                    self.object.descriptor_ui = 'D' + acronym + zseq
                except Thesaurus.DoesNotExist:
                    id_thesaurus = str(self.object.id)
                    print 'Warning! - No thesaurus_acronym for id -->',id_thesaurus
                self.object = form.save(commit=True)

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_treenumber.instance = self.object
                formset_treenumber.save()

                formset_pharmaco.instance = self.object
                formset_pharmaco.save()

                formset_related.instance = self.object
                formset_related.save()

                formset_previous.instance = self.object
                formset_previous.save()

                formset_entrycombination.instance = self.object
                formset_entrycombination.save()

                form.save()
                
                # Essas variaveis dizem respeito a criação de novo registro a partir de um termo existente
                # Quando existirem serão repassadas para a faze de criação de conceito
                if self.request.GET.get("term_ui") and self.request.GET.get("term_id"):
                    term_ui_alter = self.request.GET.get("term_ui")
                    term_id_alter = self.request.GET.get("term_id")
                    return redirect(reverse('create_concept_termdesc') + '?ths=' + self.request.GET.get("ths") + '&' + 'registry_language=' + registry_language + '&term=' + self.request.GET.get("term") + '&term_ui_alter=' + term_ui_alter + '&term_id_alter=' + term_id_alter)
                else:
                    return redirect(reverse('create_concept_termdesc') + '?ths=' + self.request.GET.get("ths") + '&' + 'registry_language=' + registry_language + '&term=' + self.request.GET.get("term"))
            else:
                if exist_tree_numbers == 0:
                    msg_erro = _("Hierarchical level")
                else:
                    msg_erro = _("already exists!!!") + ' -----> ' + tree_number_existentes
                return self.render_to_response(
                            self.get_context_data(
                                                form=form,
                                                formset_descriptor=formset_descriptor,
                                                formset_treenumber=formset_treenumber,
                                                formset_pharmaco=formset_pharmaco,
                                                formset_related=formset_related,
                                                formset_previous=formset_previous,
                                                formset_entrycombination=formset_entrycombination,
                                                msg_erro=msg_erro,
                                                )
                                            )
        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_treenumber=formset_treenumber,
                                            formset_pharmaco=formset_pharmaco,
                                            formset_related=formset_related,
                                            formset_previous=formset_previous,
                                            formset_entrycombination=formset_entrycombination,
                                            )
                                        )

    # Faz com que o forms.py tenha um pre filtro para abbreviation
    def get_form_kwargs(self):
        ths = self.request.GET.get("ths")
        kwargs = super(DescUpdate, self).get_form_kwargs()
        kwargs.update({'ths': ths})
        return kwargs

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(DescUpdate, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['language_system'] = get_language()

        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionDescFormSet(instance=self.object)
            context['formset_treenumber'] = TreeNumbersListDescFormSet(instance=self.object)
            context['formset_pharmaco'] = PharmacologicalActionListDescFormSet(instance=self.object)
            context['formset_related'] = SeeRelatedListDescFormSet(instance=self.object)
            context['formset_previous'] = PreviousIndexingListDescFormSet(instance=self.object)
            context['formset_entrycombination'] = EntryCombinationListDescFormSet(instance=self.object)

        return context


class DescCreateView(DescUpdate, CreateView):
    """
    Used as class view to create Descriptors

    """

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(DescCreateView, self).dispatch(*args, **kwargs)


class DescDeleteView(DescUpdate, DeleteView):
    """
    Used as class view to delete Descriptors
    """
    model = IdentifierDesc
    template_name = 'thesaurus/descriptor_confirm_delete.html'

    def get_success_url(self):
        # messages.success(self.request, 'is deleted')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/%s' % ths 



class TermListDescChk(LoginRequiredView, ListView):
    """
    Used to verify if already exist the term
    """
    template_name = "thesaurus/descriptor_form_step0.html"
    context_object_name = "registers"


    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(TermListDescChk, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        return object_list


    def get_context_data(self, **kwargs):
        context = super(TermListDescChk, self).get_context_data(**kwargs)

        context['choiced_thesaurus_info'] = Thesaurus.objects.filter(id=self.request.GET.get("thesaurus"))

        context['term_choiced'] = self.actions['term_string']
        context['filter_language'] = self.actions['filter_language']

        return context


    def render_to_response(self, context):
        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['term_string'] and self.actions['filter_language']:

            term_choiced = self.actions['term_string']

            # Para poder criar um termo novo, não deve existir
            # -1 - Rascunho
            # 1  - Publicado
            # 5  - Histórico

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=5,
                                )

            has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_choiced.encode('utf-8'):
                    # print 'Igual-->',t,'   -   ',term_choiced.encode('utf-8')
                    has_equal=t            

            if not has_equal:
                return redirect('/thesaurus/descriptors/new/?ths=' + self.request.GET.get("thesaurus") + '&term=' + self.actions['term_string'] + '&language_code=' + self.actions['filter_language'])

        return super(TermListDescChk, self).render_to_response(context)





class DescRegisterUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update descriptor information
    """
    model = IdentifierDesc
    template_name = 'thesaurus/descriptor_edit_register.html'
    form_class = IdentifierDescForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(DescRegisterUpdateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):

        id_register = self.object.id
        # Search ID of the first concept of the record to then search first term of the concept
        concepts_of_register = IdentifierConceptListDesc.objects.filter(identifier_id=id_register).values('id')
        id_concept = concepts_of_register[0].get('id')
        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListDesc.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( id_term, ths )

    def form_valid(self, form):
        formset_descriptor = DescriptionDescFormSet(self.request.POST, instance=self.object)
        formset_treenumber = TreeNumbersListDescFormSet(self.request.POST, instance=self.object)
        formset_pharmaco = PharmacologicalActionListDescFormSet(self.request.POST, instance=self.object)
        formset_related = SeeRelatedListDescFormSet(self.request.POST, instance=self.object)
        formset_previous = PreviousIndexingListDescFormSet(self.request.POST, instance=self.object)
        formset_entrycombination = EntryCombinationListDescFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_treenumber_valid = formset_treenumber.is_valid()
        formset_pharmaco_valid = formset_pharmaco.is_valid()
        formset_related_valid = formset_related.is_valid()
        formset_previous_valid = formset_previous.is_valid()
        formset_entrycombination_valid = formset_entrycombination.is_valid()

        if (form_valid and 
            formset_descriptor_valid and 
            formset_treenumber_valid and 
            formset_related_valid and
            formset_pharmaco_valid and
            formset_previous_valid and
            formset_entrycombination_valid
            ):


            # Verifica se foi passado algum valor para formset_treenumber
            tree_number_existentes=''
            # Utilizado para verificar se o form está totalmente vazio - o que não deve ocorrer
            form_vazio=True
            exist_tree_numbers=0
            for f in formset_treenumber:
                if f.cleaned_data is not None:
                    fields_t = f.cleaned_data
                    content_tree_number = fields_t.get('tree_number')

                    identifier_id = fields_t.get('identifier')
                    # Onde identifier_id = 'identifier': <IdentifierDesc: 34244>
                    # Exemplo
                    # ---> {'identifier': <IdentifierDesc: 34244>, 'tree_number': u'SP4.026.307.808.100', u'id': <TreeNumbersListDesc: 68760>, u'DELETE': False}
                    # Para utilizar referenciar identifier_id.id

                    # Essa variável é do cleaned_data e diz se o registro foi apagado ou não no formulário
                    # Se for True foi apagado
                    status_preenchimento = fields_t.get('DELETE')

                    if status_preenchimento == False:
                        form_vazio=False
                        exist_tree_numbers = exist_tree_numbers + 1

                        # Verifica se ja existe cadastrado o tree_number para este tesauro
                        result_tree_number = TreeNumbersListDesc.objects.filter(tree_number=content_tree_number).exclude(identifier_id=identifier_id.id).values('identifier_id')

                        if result_tree_number is not None:
                            for t in result_tree_number:
                                identifier_id_existent_tree_number = t.get('identifier_id')

                                # Checks if the record is for the thesaurus being worked on
                                res_existent_thesaurus_id = IdentifierDesc.objects.filter(id=identifier_id_existent_tree_number).values('thesaurus_id')
                                existent_thesaurus_id=res_existent_thesaurus_id[0].get('thesaurus_id')

                                # Brings id of thesaurus currently operating
                                environment_thesaurus_id = self.request.GET.get("ths")

                                # If tree_number exists in same thesaurus creates error
                                if int(environment_thesaurus_id) == int(existent_thesaurus_id):
                                    tree_number_existentes = tree_number_existentes + content_tree_number + '   '

            # Condição para poder criar registro
            if not tree_number_existentes and exist_tree_numbers > 0 and form_vazio==False:

                # Bring the choiced language_code from the first form
                registry_language = formset_descriptor.cleaned_data[0].get('language_code')

                self.object = form.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_treenumber.instance = self.object
                formset_treenumber.save()

                formset_pharmaco.instance = self.object
                formset_pharmaco.save()

                formset_related.instance = self.object
                formset_related.save()

                formset_previous.instance = self.object
                formset_previous.save()

                formset_entrycombination.instance = self.object
                formset_entrycombination.save()

                form.save()

                return HttpResponseRedirect(self.get_success_url())

            else:

                if form_vazio == True:
                    ths = self.request.GET.get("ths")
                    return redirect('/thesaurus/descriptors?ths=' + ths)

                elif exist_tree_numbers == 0:
                    msg_erro = _("Hierarchical level")
                else:
                    msg_erro = _("already exists!!!") + ' -----> ' + tree_number_existentes
                    return self.render_to_response(
                                self.get_context_data(
                                                    form=form,
                                                    formset_descriptor=formset_descriptor,
                                                    formset_treenumber=formset_treenumber,
                                                    formset_pharmaco=formset_pharmaco,
                                                    formset_related=formset_related,
                                                    formset_previous=formset_previous,
                                                    formset_entrycombination=formset_entrycombination,
                                                    msg_erro=msg_erro,
                                                    )
                                                )
        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_treenumber=formset_treenumber,
                                            formset_pharmaco=formset_pharmaco,
                                            formset_related=formset_related,
                                            formset_previous=formset_previous,
                                            formset_entrycombination=formset_entrycombination,
                                            )
                                        )

    # Makes forms.py have a pre-filter for abbreviation
    def get_form_kwargs(self):
        ths = self.request.GET.get("ths")
        kwargs = super(DescRegisterUpdateView, self).get_form_kwargs()
        kwargs.update({'ths': ths})
        return kwargs

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)

    def get_context_data(self, **kwargs):

        context = super(DescRegisterUpdateView, self).get_context_data(**kwargs)

        context['language_system'] = get_language()

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionDescFormSet(instance=self.object)
            context['formset_treenumber'] = TreeNumbersListDescFormSet(instance=self.object)
            context['formset_pharmaco'] = PharmacologicalActionListDescFormSet(instance=self.object)
            context['formset_related'] = SeeRelatedListDescFormSet(instance=self.object)
            context['formset_previous'] = PreviousIndexingListDescFormSet(instance=self.object)
            context['formset_entrycombination'] = EntryCombinationListDescFormSet(instance=self.object)

        return context



class DescListView(LoginRequiredView, ListView):
    """
    List descriptor records
    """
    template_name = "thesaurus/thesaurus_home.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE


    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            elif self.request.GET.get("ths"):
                environment_thesaurus_id=self.request.GET.get("ths")
            elif self.request.POST.get("choiced_thesaurus"):
                environment_thesaurus_id=self.request.POST.get("choiced_thesaurus")
            else:
                self.actions = {}
                for key in ACTIONS.keys():
                    self.actions[key] = self.request.GET.get(key, ACTIONS[key])
                environment_thesaurus_id=self.actions['choiced_thesaurus']

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(DescListView, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        lang_code = get_language()
        object_list = []
        registers_indexed = []
        concepts_indexed = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        # icontains X exact -------------------------------------------------------------------------------------
        if self.actions['exact']:
            q_term_string = Q(term_string__exact=self.actions['s'])
        else:
            q_term_string = Q(term_string__icontains=self.actions['s'])

        # term_string
        if self.actions['filter_fields'] == 'term_string' and self.actions['exact']:
            q_term_string = Q(term_string=self.actions['s'])
        else:
            if not self.actions['filter_fields'] and not self.actions['exact']:
                q_term_string = Q(term_string__icontains=self.actions['s'])

        # concept_preferred_term='Y'
        q_concept_preferred_term = Q(concept_preferred_term='Y')

        # record_preferred_term='Y'
        q_record_preferred_term = Q(record_preferred_term='Y')

        # status
        if self.actions['filter_status']:
            q_filter_status = Q(status=self.actions['filter_status'])


        # Term
        # AND performance for Term ------------------------------------------------------------------------
        # Do the initial search in term_string field
        if self.actions['s'] and not self.actions['filter_fields']:
            object_list = TermListDesc.objects.filter( q_term_string ).filter(term_thesaurus=self.actions['choiced_thesaurus']).exclude(status=-3).order_by('term_string')
        else:
            # bring all registers
            object_list = TermListDesc.objects.all().filter(term_thesaurus=self.actions['choiced_thesaurus']).exclude(status=-3).order_by('term_string')

        # term_string
        if self.actions['filter_fields'] == 'term_string' and self.actions['s']:
            object_list = TermListDesc.objects.filter( q_term_string ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # Concept
        # AND performance for Concept ------------------------------------------------------------------------
        # when concept_preferred_term='Y' & record_preferred_term='Y'
        if self.actions['filter_fields'] == 'concept':
            object_list = TermListDesc.objects.filter( q_term_string & q_concept_preferred_term & q_record_preferred_term ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # MESH Descriptor UI
        # AND performance for MESH Descriptor UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'descriptor_ui':
            id_register = IdentifierDesc.objects.filter(descriptor_ui=self.actions['s']).values('id')
            id_concept = IdentifierConceptListDesc.objects.filter(identifier_id=id_register,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListDesc.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])



        # DeCS Descriptor UI
        # AND performance for DeCS Descriptor UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'decs_code':
            id_register = IdentifierDesc.objects.filter(decs_code=self.actions['s']).values('id')
            id_concept = IdentifierConceptListDesc.objects.filter(identifier_id=id_register,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListDesc.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # Tree Number
        # AND performance for Tree Number --------------------------------------------------------------
        if self.actions['filter_fields'] == 'tree_number':
            id_tree_number = TreeNumbersListDesc.objects.filter(tree_number=self.actions['s']).values('identifier_id')
            id_concept = IdentifierConceptListDesc.objects.filter(identifier_id__in=id_tree_number,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListDesc.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # Concept UI
        # AND performance for Concept UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'concept_ui':
            concept_identifier_id = IdentifierConceptListDesc.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
            id_register = IdentifierDesc.objects.filter(id__in=concept_identifier_id,thesaurus_id=self.actions['choiced_thesaurus']).values('id')
            concept_id = IdentifierConceptListDesc.objects.filter(identifier_id=id_register,concept_ui=self.actions['s']).values('id')
            object_list = TermListDesc.objects.filter(identifier_concept_id=concept_id).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # order performance -------------------------------------------------------------------------------------
        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # if self.actions['visited'] != 'ok':
        # if not self.actions['visited']:
        #     object_list = object_list.none()

        return object_list


    def get_context_data(self, **kwargs):
        context = super(DescListView, self).get_context_data(**kwargs)
        context['actions'] = self.actions

        context['last_created_objects_list'] = TermListDesc.objects.filter(term_thesaurus=self.request.GET.get("ths")).exclude(status=-3).exclude(status=3).exclude(status=5).exclude(date_created__isnull=True).order_by('-date_created','-id')[:10][::-1]
        context['last_altered_objects_list'] = TermListDesc.objects.filter(term_thesaurus=self.request.GET.get("ths")).exclude(status=-3).exclude(date_altered__isnull=True).order_by('-date_altered','-id')[:10][::-1]

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context




# FORM 2
# Creates concept and term
class ConceptTermUpdate(LoginRequiredView):

    """
    Used as class view to create ConceptTermUpdate
    Extend ConceptTermUpdate that do all the work
    Create the second form
    """
    model = IdentifierConceptListDesc
    form_class = IdentifierConceptListDescForm
    template_name = 'thesaurus/descriptor_form_step2.html'

    def form_valid(self, form):

        formset_concept = ConceptListDescFormSet(self.request.POST, instance=self.object)
        formset_term = TermListDescFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_concept_valid and formset_term_valid):
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("termdesc-0-term_string")
            language_code = self.request.POST.get("termdesc-0-language_code")
            term_thesaurus = self.request.GET.get("ths")

            # Se existirem essas variaveis não deverá ser realizado a verificação de existência pois nesse caso 
            # será forçado a criação de novo registro, e o registro antigo será alterado seu status
            if self.request.GET.get("term_ui_alter") and self.request.GET.get("term_id_alter"):

                self.object = form.save()

                # Get thesaurus_acronym to create new ID format to concept_ui field
                self.object = form.save(commit=False)
                zseq = str(self.object.id).zfill(8) # preenche zeros a esquerda
                self.object.concept_ui = 'FD' + zseq
                self.object = form.save(commit=True)

                formset_concept.instance = self.object
                formset_concept.save()

                formset_term.instance = self.object
                formset_term.save()

                # Bring the choiced language_code from the first form
                registry_language = formset_term.cleaned_data[0].get('language_code')

                # Update the created term_ui with a old content - term_ui_alter
                try:
                    created_id = int(TermListDesc.objects.latest('id').id)
                    update_field = TermListDesc.objects.get(id=created_id)
                    update_field.term_ui = self.request.GET.get("term_ui_alter")

                    # descobre id do conceito que o termo antigo pertence
                    identifier_concept_id = TermListDesc.objects.filter(id=self.request.GET.get("term_id_alter")).values('identifier_concept_id')
                    identifier_concept_id = identifier_concept_id[0].get('identifier_concept_id')

                    # descobre concept_ui
                    concept_ui_origem = IdentifierConceptListDesc.objects.filter(id=identifier_concept_id).values('concept_ui')
                    concept_ui_origem = concept_ui_origem[0].get('concept_ui')

                    # coleta informação do histórico do term antigo
                    historical_annotation_old=TermListDesc.objects.filter(id=self.request.GET.get("term_id_alter")).values('historical_annotation')
                    if len(historical_annotation_old) > 0:
                        historical_annotation_old=historical_annotation_old[0].get('historical_annotation')
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
                    else:
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8')

                    update_field.historical_annotation = historical_annotation_new

                    update_field.save()

                except TermListDesc.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                # Update old term register, status and historical_annotation - term_id_alter
                try:
                    # Busca informação do concept_ui do novo termo
                    created_id = int(TermListDesc.objects.latest('id').id)

                    # descobre id do conceito que o termo antigo pertence
                    identifier_concept_id = TermListDesc.objects.filter(id=created_id).values('identifier_concept_id')
                    identifier_concept_id = identifier_concept_id[0].get('identifier_concept_id')

                    # descobre concept_ui
                    concept_ui_destino = IdentifierConceptListDesc.objects.filter(id=identifier_concept_id).values('concept_ui')
                    concept_ui_destino = concept_ui_destino[0].get('concept_ui')                    

                    # coleta informação do histórico do term antigo
                    historical_annotation_old=TermListDesc.objects.filter(id=self.request.GET.get("term_id_alter")).values('historical_annotation')
                    if len(historical_annotation_old) > 0:
                        historical_annotation_old=historical_annotation_old[0].get('historical_annotation')
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - sent to ' + concept_ui_destino
                        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
                    else:
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - sent to ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8')

                    update_field = TermListDesc.objects.get(id=self.request.GET.get("term_id_alter"))
                    update_field.status = '-3'
                    update_field.historical_annotation = historical_annotation_new

                    update_field.save()
                except TermListDesc.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                form.save()

                return HttpResponseRedirect(self.get_success_url())

            else:           
                has_term = TermListDesc.objects.filter(
                    term_string__exact=term_string,
                    language_code=language_code,
                    term_thesaurus=term_thesaurus,
                    status=1,
                    ).exists()

                if not has_term:

                    self.object = form.save()

                    # Get thesaurus_acronym to create new ID format to concept_ui field
                    self.object = form.save(commit=False)
                    zseq = str(self.object.id).zfill(8) # preenche zeros a esquerda
                    self.object.concept_ui = 'FD' + zseq
                    self.object = form.save(commit=True)

                    formset_concept.instance = self.object
                    formset_concept.save()

                    formset_term.instance = self.object
                    formset_term.save()

                    # Bring the choiced language_code from the first form
                    registry_language = formset_term.cleaned_data[0].get('language_code')

                    # Update term_ui with a new format
                    try:

                        ths = self.request.GET.get("ths")
                        try:
                            seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                            nseq = str(int(seq.sequential_number) + 1)
                            seq.sequential_number = nseq
                            seq.save()
                        except code_controller_term.DoesNotExist:
                            seq = code_controller_term(sequential_number=1,thesaurus=ths)
                            nseq = 1
                            seq.save()
                        created_id = int(TermListDesc.objects.latest('id').id)
                        update_field = TermListDesc.objects.get(id=created_id)

                        # substitui idioma do sistema por sigla de 3 letras
                        if registry_language == 'en':
                            language_3letters = 'eng'
                        if registry_language == 'es':
                            language_3letters = 'spa'
                        if registry_language == 'pt-br':
                            language_3letters = 'por'
                        if registry_language == 'fr':
                            language_3letters = 'fre'
                        if registry_language == 'es-es':
                            language_3letters = 'spa'

                        # preenche zeros a esquerda
                        zseq = str(nseq).zfill(6)

                        update_field.term_ui = language_3letters + 'd' + zseq
                        update_field.save()
                    except TermListDesc.DoesNotExist:
                        print 'Warning! Does not exist id to this Term'

                    form.save()

                    return HttpResponseRedirect(self.get_success_url())
                else:
                    msg_erro =  _("This Concept already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                    form=form,
                                                    formset_concept=formset_concept,
                                                    formset_term=formset_term,
                                                    msg_erro=msg_erro,
                                                    ))

        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_concept=formset_concept,
                                            formset_term=formset_term,
                                            )
                                        )

    def get_context_data(self, **kwargs):
        context = super(ConceptTermUpdate, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['language_system'] = get_language()

        if IdentifierDesc.objects.count() > 0:
            context['next_id'] = int(IdentifierDesc.objects.latest('id').id)
        else:
            context['next_id'] = 1


        if self.request.method == 'GET':

            context['formset_concept'] = ConceptListDescFormSet(instance=self.object)
            context['formset_term'] = TermListDescFormSet(instance=self.object)

        return context



class DescCreateView2(ConceptTermUpdate, CreateView):
    """
    Used as class view to create Descriptors
    """
    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(DescCreateView2, self).dispatch(*args, **kwargs)


    def get_success_url(self):
        # messages.success(self.request, 'is created')

        id_concept = self.object.id
        # Pesquisa ID do primeiro termo deste conceito para redirecionar
        terms_of_concept = TermListDesc.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( id_term, ths )



# Pesquisa ID do registro para poder saber qual é o ID do conceito destino
class ConceptListDescView(LoginRequiredView, ListView):
    """
    List descriptor records (used by relationship popup selection window)
    """
    template_name = "thesaurus/search_concept_desc.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['choiced_concept_identifier_id']:
            concept_identifier_id = self.actions['choiced_concept_identifier_id']

        if self.actions['s']:
            try:
                id_registro = IdentifierDesc.objects.filter(descriptor_ui=self.actions['s'],thesaurus=self.request.GET.get("ths")).values('id')
                if len(id_registro)>0:
                    id_registro = id_registro[0].get('id')
                    # Força somente 1 resultado
                    object_list = IdentifierConceptListDesc.objects.filter(identifier_id=id_registro).values('identifier_id','termdesc__term_string','termdesc__language_code','termdesc__id')[:1]
            except IdentifierDesc.DoesNotExist:
                # order performance -------------------------------------------------------------------------------------
                if self.actions['order'] == "-":
                    object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

                if self.actions['visited'] != 'ok':
                    object_list = object_list.none()


        return object_list

    def get_context_data(self, **kwargs):
        context = super(ConceptListDescView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['actions'] = self.actions

        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['s']:
            try:
                # Força somente 1 resultado
                id_registro = IdentifierDesc.objects.filter(descriptor_ui=self.actions['s'],thesaurus=self.request.GET.get("ths")).values('id')[:1]

                # IdentifierDesc
                context['id_register_objects'] = IdentifierDesc.objects.filter(
                                                id=id_registro,
                                                ).values(
                                                    # IdentifierDesc
                                                    'id',
                                                    'thesaurus',
                                                    'descriptor_class',
                                                    'descriptor_ui',
                                                    'decs_code',
                                                    'external_code',
                                                    'nlm_class_number',
                                                    'date_created',
                                                    'date_revised',
                                                    'date_established',
                                                    'abbreviation',
                                                )
                context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

            except IdentifierDesc.DoesNotExist:
                context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

        return context



def ConceptListDescModification(request,term_id, ths, concept_ori):

    # Descobre qual é o id do conceito do termo destino
    id_concept_destino = TermListDesc.objects.filter(id=term_id).values('identifier_concept_id')
    id_concept_destino = id_concept_destino[0].get('identifier_concept_id')

    identifier_id_destino = IdentifierConceptListDesc.objects.filter(id=id_concept_destino).values('identifier_id')
    identifier_id_destino = identifier_id_destino[0].get('identifier_id')

    # Verifica se o conceito é preferido, se for deverá ser escolhido o proximo nao preferido que assumirá a predileção
    check_preferred_concept_origem = IdentifierConceptListDesc.objects.filter(id=concept_ori).values('preferred_concept')
    check_preferred_concept_origem = check_preferred_concept_origem[0].get('preferred_concept')

    # Como o registro em TermListDesc será nao preferido, record_preferred_term deverá ser N obrigatoriamente no destino
    # Para isso, devo trazer todos os registros de concept_ori e atualizá-los
    TermListDesc.objects.filter(identifier_concept_id=concept_ori).update(record_preferred_term='N')

    if check_preferred_concept_origem == 'Y':

        # Verifica se o conceito origem tem irmãos, se houver e se o conceito origem for preferido então o segundo conceito assumirá a predileção
        check_concept_id_origem = IdentifierConceptListDesc.objects.filter(id=concept_ori).values('identifier_id')
        check_concept_id_origem = check_concept_id_origem[0].get('identifier_id')

        check_concept_id_origem = IdentifierConceptListDesc.objects.filter(identifier_id=check_concept_id_origem).values('identifier_id')

        if len(check_concept_id_origem) > 1:

            # Descobre qual o id do primeiro registro nao preferido
            check_concept_id_not_preferred = IdentifierConceptListDesc.objects.filter(identifier_id=check_concept_id_origem,preferred_concept='N').values('id')
            check_concept_id_not_preferred = check_concept_id_not_preferred[0].get('id')

            # Atualiza o status do conceito para preferred_concept='Y'
            IdentifierConceptListDesc.objects.filter(id=check_concept_id_not_preferred).update(concept_relation_name='',preferred_concept='Y')

            # Necessário atualizar também os termos que são preferidos no conceito para também preferidos do registro
            TermListDesc.objects.filter(identifier_concept_id=check_concept_id_not_preferred, concept_preferred_term='Y').update(record_preferred_term='Y')


    # Atualiza o identifier_id do conceito antigo para novo numero identifier_id_destino
    # Atualiza o campo de histórico gravando informação de que registro foi originado
    identifier_id_ori = IdentifierConceptListDesc.objects.filter(id=concept_ori).values('identifier_id')
    identifier_id_ori = identifier_id_ori[0].get('identifier_id')
    descriptor_ui_ori = IdentifierDesc.objects.filter(id=identifier_id_ori).values('descriptor_ui')
    descriptor_ui_ori = descriptor_ui_ori[0].get('descriptor_ui')

    # Verifica se já existe anotação no historico
    has_hist=IdentifierConceptListDesc.objects.filter(id=concept_ori).exclude(historical_annotation__isnull=True).exclude(historical_annotation='').values('id','historical_annotation')
    if len(has_hist)>0:
        historical_annotation_old=has_hist[0].get('historical_annotation')
        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + str(descriptor_ui_ori)
        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
    else:
        historical_annotation_new=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + str(descriptor_ui_ori)

    IdentifierConceptListDesc.objects.filter(id=concept_ori).update(identifier_id=identifier_id_destino,concept_relation_name='NRW',preferred_concept='N', historical_annotation=historical_annotation_new)


    url = '/thesaurus/descriptors/view/' + term_id + '?ths=' + ths
    return HttpResponseRedirect(url)



# Pesquisa conceito para poder trazer ID do registro para novo conceito
# Não está sendo utilizado por enquanto
class TermListDescView(LoginRequiredView, ListView):
    """
    List descriptor records (used by relationship popup selection window)
    """
    template_name = "thesaurus/search_term_desc.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['choiced_concept_identifier_id']:
            concept_identifier_id = self.actions['choiced_concept_identifier_id']

        if self.actions['s']:
            try:
                # Como o concept_ui pode existir em mais de um tesauro devemos descobrir qual o id em IdentifierDesc que é pertinente ao tesauro em questão
                concepts = IdentifierConceptListDesc.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
                for x in concepts:
                    id_identifier = x.get('identifier_id')
                    has_register = IdentifierDesc.objects.filter(id=id_identifier,thesaurus_id=self.request.GET.get("ths")).exists()
                    if has_register:
                        # Força somente 1 resultado
                        object_list = IdentifierConceptListDesc.objects.filter(concept_ui=self.actions['s'],identifier_id=id_identifier).values('identifier_id','termdesc__term_string','termdesc__language_code','termdesc__id')[:1]

            except IdentifierConceptListDesc.DoesNotExist:
                # order performance -------------------------------------------------------------------------------------
                if self.actions['order'] == "-":
                    object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

                if self.actions['visited'] != 'ok':
                    object_list = object_list.none()

        return object_list

    def get_context_data(self, **kwargs):
        context = super(TermListDescView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['actions'] = self.actions

        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['s']:
            try:
                concepts = IdentifierConceptListDesc.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
                for x in concepts:
                    id_identifier = x.get('identifier_id')
                    has_register = IdentifierDesc.objects.filter(id=id_identifier,thesaurus_id=self.request.GET.get("ths")).exists()
                    if has_register:
                        # print 'ID pertinente',id_identifier

                        # IdentifierDesc
                        context['id_register_objects'] = IdentifierConceptListDesc.objects.filter(
                                                        concept_ui=self.actions['s'],identifier_id=id_identifier
                                                        ).values(
                                                            # IdentifierConceptListDesc
                                                            'id',
                                                            'concept_ui',
                                                        )
                        context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

            except IdentifierDesc.DoesNotExist:
                context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

        return context



def TermListDescModification(request,term_id, ths, term_ori):

    # Descobre qual é o identifier_concept_id do termo destino
    id_concept_destino = TermListDesc.objects.filter(id=term_id).values('identifier_concept_id')

    # Descobre qual é o identifier_id do conceito
    identifier_id_destino = IdentifierConceptListDesc.objects.filter(id=id_concept_destino).values('identifier_id')
    identifier_id_destino = identifier_id_destino[0].get('identifier_id')
    id_concept_destino = id_concept_destino[0].get('identifier_concept_id')

    # Descobre qual é o identifier_concept_id do termo origem
    term_origem_values = TermListDesc.objects.filter(id=term_ori).values('identifier_concept_id','term_ui')
    id_concept_origem = term_origem_values[0].get('identifier_concept_id')
    term_ui_origem = term_origem_values[0].get('term_ui')

    qtd_id_concept_origem = TermListDesc.objects.filter(identifier_concept_id=id_concept_origem)
    if len(qtd_id_concept_origem) == 1:
        # Quando existe apenas um termo para o conceito, deverá ser atualizado para a informação do novo conceito:
        # termlistdesc --> campo identifier_concept_id --> recebe valor do identifier_concept_id do termo destino
        # identifierconceptlistdesc --> campo identifier_id --> recebe o valor do identifier_id do conceito destino

        # Atualiza o identifier_id do conceito antigo para novo numero identifier_id_destino
        IdentifierConceptListDesc.objects.filter(id=id_concept_origem).update(identifier_id=identifier_id_destino,concept_relation_name='NRW',preferred_concept='N')

    # Atualiza informações do termo origem e destino
    # Prepara informacoes do historico origem
    concept_ui_origem = IdentifierConceptListDesc.objects.filter(id=id_concept_origem).values('concept_ui')
    concept_ui_origem = concept_ui_origem[0].get('concept_ui')
    historical_annotation_old=TermListDesc.objects.filter(id=term_ori).values('id','historical_annotation')
    historical_annotation_old=historical_annotation_old[0].get('historical_annotation')

    # Armazena informacao para histórico destino
    historical_annotation_old_origem=historical_annotation_old

    # Prepara informacoes do historico destino
    concept_ui_destino = IdentifierConceptListDesc.objects.filter(id=id_concept_destino).values('concept_ui')
    concept_ui_destino = concept_ui_destino[0].get('concept_ui')
    historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', sent to ' + concept_ui_destino
    historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')

    # Atualiza historico da origem
    TermListDesc.objects.filter(id=term_ori).update(status=-3,historical_annotation=historical_annotation_new, date_altered=datetime.datetime.now().strftime('%Y-%m-%d'))

    # Pesquisa a existencia de um registro existente no destino com o status de migracao - 3
    # para isso pesquisa o term_ui de origem e o status=-3
    new_term=TermListDesc.objects.filter(id=term_ori).values('status','term_ui','language_code','term_string','concept_preferred_term','is_permuted_term','lexical_tag','record_preferred_term','entry_version','date_created','date_altered','historical_annotation','term_thesaurus','identifier_concept_id',)
    term_ui_ori=new_term[0].get('term_ui')
    term_string_ori=new_term[0].get('term_string').encode('utf-8')
    
    exist_term=TermListDesc.objects.filter(status=-3, term_ui=term_ui_ori, term_string=term_string_ori, identifier_concept_id=id_concept_destino).values('id','historical_annotation')

    if len(exist_term) > 0:
        term_id_exist=exist_term[0].get('id')
        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + concept_ui_origem
        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')


        # Atualiza o historico do destino
        TermListDesc.objects.filter(id=term_id_exist).update(status='1',concept_preferred_term='N',is_permuted_term='N',record_preferred_term='N',historical_annotation=historical_annotation_new, date_altered=datetime.datetime.now().strftime('%Y-%m-%d'))

    else:
        # Cria nova entrada
        item = TermListDesc.objects.create(
                status='1',
                term_ui=new_term[0].get('term_ui'),
                language_code=new_term[0].get('language_code'),
                term_string=new_term[0].get('term_string'),
                concept_preferred_term='N',
                is_permuted_term='N',
                lexical_tag=new_term[0].get('lexical_tag'),
                record_preferred_term='N',
                entry_version=new_term[0].get('entry_version'),
                date_created=new_term[0].get('date_created'),
                date_altered=datetime.datetime.now().strftime('%Y-%m-%d'),
                historical_annotation=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + concept_ui_origem + ';' + historical_annotation_old_origem,
                term_thesaurus=new_term[0].get('term_thesaurus'),
                identifier_concept_id=id_concept_destino,
                )

    url = '/thesaurus/descriptors/view/' + term_ori + '?ths=' + ths

    return HttpResponseRedirect(url)



class TermCreateDescConfirm(LoginRequiredView, TemplateView):

    template_name = 'thesaurus/confirm_create_desc.html'

    def get_context_data(self, **kwargs):
        context = super(TermCreateDescConfirm, self).get_context_data(**kwargs)
        thesaurus_name = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_name')
        context['thesaurus_name'] = thesaurus_name[0].get('thesaurus_name')

        return context



def TermCreateDescDo(request, ths):

    term_string = request.GET.get("term_string")
    language_code = request.GET.get("language_code")
    term_ui = request.GET.get("term_ui")
    term_id = request.GET.get("term_id")

    return redirect('/thesaurus/descriptors/new/?ths=' + ths + '&term=' + term_string + '&language_code=' + language_code + '&term_ui=' + term_ui + '&term_id=' + term_id)



class ConceptCreateDescConfirm(LoginRequiredView, TemplateView):

    template_name = 'thesaurus/confirm_create_register_desc.html'

    def get_context_data(self, **kwargs):
        context = super(ConceptCreateDescConfirm, self).get_context_data(**kwargs)
        thesaurus_name = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_name')
        context['thesaurus_name'] = thesaurus_name[0].get('thesaurus_name')

        return context



def ConceptCreateDescDo(request, ths):

    term_string = request.GET.get("term_string")
    language_code = request.GET.get("language_code")
    concept_id = request.GET.get("concept_id")
    term_id = request.GET.get("term_id")
    created_by = request.GET.get("created_by")

    # Descobrindo qual é o descriptor_ui do registro origem
    identifier_id_ori = IdentifierConceptListDesc.objects.filter(id=concept_id).values('identifier_id')
    identifier_id_ori = identifier_id_ori[0].get('identifier_id')
    descriptor_ui_ori = IdentifierDesc.objects.filter(id=identifier_id_ori).values('descriptor_ui')
    descriptor_ui_ori = descriptor_ui_ori[0].get('descriptor_ui')

    # Verifica se já existe anotação no historico
    has_hist=IdentifierConceptListDesc.objects.filter(id=concept_id).values('historical_annotation')
    if has_hist:
        historical_annotation_old=has_hist[0].get('historical_annotation')
        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + str(descriptor_ui_ori)
        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')

    created_time=datetime.datetime.now().strftime('%Y-%m-%d')
    created_time = created_time.encode('utf-8')

    # Get sequential number to write to decs_code
    try:
        seq = code_controller.objects.get(thesaurus=ths)
        nseq = str(int(seq.sequential_number) + 1)
        seq.sequential_number = nseq
        seq.save()
    except code_controller.DoesNotExist:
        seq = code_controller(sequential_number=1,thesaurus=ths)
        nseq = 1
        seq.save()
    decs_code=nseq

    # Get thesaurus_acronym to create new ID format to descriptor_ui field
    try:
        acronym = Thesaurus.objects.filter(id=ths).values('thesaurus_acronym')
        # recupera o acronimo e transforma em maiusuclo
        acronym = str(acronym[0].get('thesaurus_acronym')).upper()
        # utiliza self.object.decs_code para compor descriptor_ui
        zseq = str(nseq).zfill(6) # preenche zeros a esquerda
        descriptor_ui = 'D' + acronym + zseq
    except Thesaurus.DoesNotExist:
        id_thesaurus = str(self.object.id)
        print 'Warning! - No thesaurus_acronym for id -->',id_thesaurus

    add_reg = IdentifierDesc(descriptor_class='', descriptor_ui=descriptor_ui, decs_code=decs_code, external_code='', nlm_class_number='', date_created=created_time, created_by_id=created_by, thesaurus_id=ths)
    add_reg.save()

    # Descobrindo último ID inserido
    last_id = IdentifierDesc.objects.filter(thesaurus_id=ths).order_by('id').last()
    # print '[last_id - ' ,last_id,' ]'

    # Atualiza identifier_id antigo para novo id, apaga concept_relation_name, atualiza preferred_concept como preferido e atualiza hsitórico
    update_field = IdentifierConceptListDesc.objects.get(id=concept_id)
    update_field.identifier_id = last_id
    update_field.concept_relation_name = ""
    update_field.preferred_concept = "Y"
    update_field.historical_annotation = historical_annotation_new
    update_field.save()

    # Atualiza record_preferred_term dos Termos que foram elegidos como preferidos no registro novo
    update_registers = TermListDesc.objects.filter(identifier_concept_id=concept_id, concept_preferred_term='Y', record_preferred_term='N')
    # print '[ DEBUG]', update_registers
    if update_registers:
        for upd in update_registers:
            # print '---> ',upd
            TermListDesc.objects.filter(id=str(upd)).update(record_preferred_term='Y')

    return redirect('/thesaurus/descriptors/view/' + term_id + '?ths=' + ths)



class ConceptListDescCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create Concept and Term
    """
    model = IdentifierConceptListDesc
    template_name = 'thesaurus/descriptor_new_concept.html'
    form_class = IdentifierConceptListDescForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(ConceptListDescCreateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):

        id_concept = self.object.id

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListDesc.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( id_term, ths )

    def form_valid(self, form):

        formset_concept = ConceptListDescFormSet(self.request.POST, instance=self.object)
        formset_term = TermListDescFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_concept_valid and formset_term_valid):
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("termdesc-0-term_string")
            language_code = self.request.POST.get("termdesc-0-language_code")
            term_thesaurus = self.request.GET.get("ths")

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=5,
                                )

            has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_string.encode('utf-8'):
                    # print 'Igual-->',t
                    has_equal=t

            if not has_equal:

                self.object = form.save(commit=False)
                self.object.identifier_id = int(self.request.POST.get("identifier_id"))
                self.object = form.save(commit=True)

                formset_concept.instance = self.object
                formset_concept.save()

                formset_term.instance = self.object
                formset_term.save()

                # Bring the choiced language_code from the first form
                registry_language = formset_term.cleaned_data[0].get('language_code')

                form.save()

                # Update concept_ui with a new format
                try:
                    created_concept_id = int(IdentifierConceptListDesc.objects.latest('id').id)
                    update_concept_field = IdentifierConceptListDesc.objects.get(id=created_concept_id)

                    # preenche zeros a esquerda
                    zseq = str(created_concept_id).zfill(8)

                    update_concept_field.concept_ui = 'FD' + zseq
                    update_concept_field.save()
                except IdentifierConceptListDesc.DoesNotExist:
                    print 'Warning! Does not exist id to this Concept'

                # Update term_ui with a new format
                try:

                    ths = self.request.GET.get("ths")
                    try:
                        seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                        nseq = str(int(seq.sequential_number) + 1)
                        seq.sequential_number = nseq
                        seq.save()
                    except code_controller_term.DoesNotExist:
                        seq = code_controller_term(sequential_number=1,thesaurus=ths)
                        nseq = 1
                        seq.save()
                    created_id = int(TermListDesc.objects.latest('id').id)
                    update_field = TermListDesc.objects.get(id=created_id)

                    # substitui idioma do sistema por sigla de 3 letras
                    if registry_language == 'en':
                        language_3letters = 'eng'
                    if registry_language == 'es':
                        language_3letters = 'spa'
                    if registry_language == 'pt-br':
                        language_3letters = 'por'
                    if registry_language == 'fr':
                        language_3letters = 'fre'
                    if registry_language == 'es-es':
                        language_3letters = 'spa'

                    # preenche zeros a esquerda
                    zseq = str(nseq).zfill(6)

                    update_field.term_ui = language_3letters + 'd' + zseq
                    update_field.save()
                except TermListDesc.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                # Update created_date
                try:
                    created_id = int(TermListDesc.objects.latest('id').id)
                    update_date_created = TermListDesc.objects.get(id=created_id)
                    update_date_created.date_created = datetime.datetime.now().strftime('%Y-%m-%d')
                    update_date_created.save()
                except TermListDesc.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                return HttpResponseRedirect(self.get_success_url())
            else:
                msg_erro =  _("This Concept already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                form=form,
                                                formset_concept=formset_concept,
                                                formset_term=formset_term,
                                                msg_erro=msg_erro,
                                                ))

    def get_context_data(self, **kwargs):
        context = super(ConceptListDescCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.method == 'GET':
            context['formset_concept'] = ConceptListDescFormSet(instance=self.object)
            context['formset_term'] = TermListDescFormSet(instance=self.object)

        return context



class ConceptListDescUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update concept
    """
    model = IdentifierConceptListDesc
    template_name = 'thesaurus/descriptor_edit_concept.html'
    form_class = IdentifierConceptListDescForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(ConceptListDescUpdateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( int(self.request.POST.get("termdesc__id")), ths )

    def form_valid(self, form):

        formset_concept = ConceptListDescFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()

        if (form_valid and formset_concept_valid):

            self.object = form.save(commit=False)
            self.object.identifier_id = int(self.request.POST.get("identifier_id"))
    
            formset_concept.instance = self.object
            formset_concept.save()

            form.save()

            # Necessário atualizar também os termos que são preferidos no conceito para também preferidos do registro
            # print 'id ----->',self.object.id
            check_preferred_concept = self.request.POST.get("preferred_concept")
            # print 'check_preferred_concept ---->',check_preferred_concept

            if check_preferred_concept == 'Y':
                TermListDesc.objects.filter(identifier_concept_id=self.object.id, concept_preferred_term='Y').update(record_preferred_term='Y')
            else:
                TermListDesc.objects.filter(identifier_concept_id=self.object.id, concept_preferred_term='Y').update(record_preferred_term='N')

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                            form=form,
                                            formset_concept=formset_concept,
                                            )
                        )

    def get_context_data(self, **kwargs):
        context = super(ConceptListDescUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.method == 'GET':
            context['formset_concept'] = ConceptListDescFormSet(instance=self.object)
        return context




class TermListDescCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create TermListDesc
    """
    # model = TermListDesc
    template_name = 'thesaurus/descriptor_new_term.html'
    form_class = TermListDescUniqueForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(TermListDescCreateView, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(TermListDescCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.POST:
            context['formset_toccurrence'] = TheraurusOccurrenceListDescFormSet(self.request.POST)
        else:
            context['formset_toccurrence'] = TheraurusOccurrenceListDescFormSet()
        return context

    def form_valid(self, form):
        
        formset_toccurrence = TheraurusOccurrenceListDescFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_toccurrence_valid = formset_toccurrence.is_valid()

        if (form_valid and formset_toccurrence_valid):
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("term_string")
            language_code = self.request.POST.get("language_code")
            concept_preferred_term = self.request.POST.get("concept_preferred_term")
            record_preferred_term = self.request.POST.get("record_preferred_term")
            identifier_concept_id = self.request.POST.get("identifier_concept_id")
            term_thesaurus = self.request.GET.get("ths")

            if concept_preferred_term == 'Y' and record_preferred_term == 'Y':
                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by published record
                q_status_published = Q(
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    concept_preferred_term="Y",
                                    record_preferred_term="Y",
                                    identifier_concept_id=identifier_concept_id,
                                    # status=1,
                                    )

            if concept_preferred_term == 'Y' and record_preferred_term == 'N':
                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by published record
                q_status_published = Q(
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    concept_preferred_term="Y",
                                    record_preferred_term="N",
                                    identifier_concept_id=identifier_concept_id,
                                    # status=1,
                                    )

            if ( concept_preferred_term == 'Y' and record_preferred_term == 'Y' ) or ( concept_preferred_term == 'Y' and record_preferred_term == 'N' ):

                has_term_config = TermListDesc.objects.filter( q_status_published ).values('id')

                if len(has_term_config) > 0:

                    msg_erro =  _("This configuration already exists for this concept!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        formset_toccurrence=formset_toccurrence,
                                                                        msg_erro=msg_erro,
                                                                        ))
                else:

                    # Para poder criar um termo novo, não deve existir
                    # -1 - Rascunho
                    # 1  - Publicado
                    # 5  - Histórico

                    # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                    # Search by draft record
                    q_status_draft = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=-1,
                                        )

                    # Search by published record
                    q_status_published = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=1,
                                        )

                    # Search by historical record
                    q_status_historical = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=5,
                                        )

                    has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

                    # Corre resultados e compara
                    has_equal=''
                    for term in has_term:
                        t=term.get('term_string').encode('utf-8')
                        if t == term_string.encode('utf-8'):
                            # print 'Igual-->',t
                            has_equal=t

                    if not has_equal:

                        self.object = form.save(commit=False)

                        # prove the current date if you are not informed on the form
                        if not self.object.date_created:
                            self.object.date_created = datetime.datetime.now().strftime('%Y-%m-%d')

                        self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")
                        self.object = form.save(commit=True)

                        formset_toccurrence.instance = self.object
                        formset_toccurrence.save()

                        form.save()

                        registry_language = self.request.POST.get("language_code")

                        # Update term_ui with a new format
                        try:

                            ths = self.request.GET.get("ths")
                            try:
                                seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                                nseq = str(int(seq.sequential_number) + 1)
                                seq.sequential_number = nseq
                                seq.save()
                            except code_controller_term.DoesNotExist:
                                seq = code_controller_term(sequential_number=1,thesaurus=ths)
                                nseq = 1
                                seq.save()
                            created_id = int(TermListDesc.objects.latest('id').id)
                            update_field = TermListDesc.objects.get(id=created_id)

                            # substitui idioma do sistema por sigla de 3 letras
                            if registry_language == 'en':
                                language_3letters = 'eng'
                            if registry_language == 'es':
                                language_3letters = 'spa'
                            if registry_language == 'pt-br':
                                language_3letters = 'por'
                            if registry_language == 'fr':
                                language_3letters = 'fre'
                            if registry_language == 'es-es':
                                language_3letters = 'spa'

                            # preenche zeros a esquerda
                            zseq = str(nseq).zfill(6)

                            update_field.term_ui = language_3letters + 'd' + zseq
                            update_field.save()
                        except TermListDesc.DoesNotExist:
                            print 'Warning! Does not exist id to this Term'

                        return HttpResponseRedirect(self.get_success_url())
                    else:

                        msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                        return self.render_to_response(self.get_context_data(
                                                                            form=form,
                                                                            formset_toccurrence=formset_toccurrence,
                                                                            msg_erro=msg_erro,
                                                                            ))

            else:

                # Para poder criar um termo novo, não deve existir
                # -1 - Rascunho
                # 1  - Publicado
                # 5  - Histórico

                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by draft record
                q_status_draft = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=-1,
                                    )

                # Search by published record
                q_status_published = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=1,
                                    )

                # Search by historical record
                q_status_historical = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=5,
                                    )

                has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

                # Corre resultados e compara
                has_equal=''
                for term in has_term:
                    t=term.get('term_string').encode('utf-8')
                    if t == term_string.encode('utf-8'):
                        # print 'Igual-->',t
                        has_equal=t

                if not has_equal:
                    self.object = form.save(commit=False)

                    # prove the current date if you are not informed on the form
                    if not self.object.date_created:
                        self.object.date_created = datetime.datetime.now().strftime('%Y-%m-%d')

                    self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")
                    self.object = form.save(commit=True)

                    formset_toccurrence.instance = self.object
                    formset_toccurrence.save()

                    form.save()

                    registry_language = self.request.POST.get("language_code")

                    # Update term_ui with a new format
                    try:

                        ths = self.request.GET.get("ths")
                        try:
                            seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                            nseq = str(int(seq.sequential_number) + 1)
                            seq.sequential_number = nseq
                            seq.save()
                        except code_controller_term.DoesNotExist:
                            seq = code_controller_term(sequential_number=1,thesaurus=ths)
                            nseq = 1
                            seq.save()
                        created_id = int(TermListDesc.objects.latest('id').id)
                        update_field = TermListDesc.objects.get(id=created_id)

                        # substitui idioma do sistema por sigla de 3 letras
                        if registry_language == 'en':
                            language_3letters = 'eng'
                        if registry_language == 'es':
                            language_3letters = 'spa'
                        if registry_language == 'pt-br':
                            language_3letters = 'por'
                        if registry_language == 'fr':
                            language_3letters = 'fre'
                        if registry_language == 'es-es':
                            language_3letters = 'spa'

                        # preenche zeros a esquerda
                        zseq = str(nseq).zfill(6)

                        update_field.term_ui = language_3letters + 'd' + zseq
                        update_field.save()
                    except TermListDesc.DoesNotExist:
                        print 'Warning! Does not exist id to this Term'

                    return HttpResponseRedirect(self.get_success_url())
                else:
                    msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        formset_toccurrence=formset_toccurrence,
                                                                        msg_erro=msg_erro,
                                                                        ))
    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( self.object.id, ths )




class TermListDescUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update Term
    """
    model = TermListDesc
    template_name = 'thesaurus/descriptor_edit_term.html'
    form_class = TermListDescUniqueForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(TermListDescUpdateView, self).dispatch(*args, **kwargs)


    def form_valid(self, form):

        formset_toccurrence = TheraurusOccurrenceListDescFormSet(self.request.POST, instance=self.object)

        # Armazena string de term_string para popular historico
        term_string_current = TermListDesc.objects.filter(id=self.object.id).values('term_string','concept_preferred_term','record_preferred_term','historical_annotation')
        for y in term_string_current:
            term_string_old=y.get('term_string')
            concept_preferred_term_old=y.get('concept_preferred_term')
            record_preferred_term_old=y.get('record_preferred_term')
            historical_annotation_old=y.get('historical_annotation')
            # print 'Current - TERM ----->',term_string_old
            # print 'Current - Historico --->',historical_annotation_old

        # Brings form variables to check if it already exists
        term_string = self.request.POST.get("term_string")

        language_code = self.request.POST.get("language_code")
        concept_preferred_term = self.request.POST.get("concept_preferred_term")
        record_preferred_term = self.request.POST.get("record_preferred_term")
        identifier_concept_id = self.request.POST.get("identifier_concept_id")
        term_thesaurus = self.request.GET.get("ths")

        # Username
        user_data = additional_user_info(self.request)
        for user_name in user_data:
            username=user_data.get('user_name').encode('utf-8')
            break

        v998='^d' + datetime.datetime.now().strftime('%Y-%m-%d') + '^h' + term_string_old + '^u' + username + '^t'

        # Se ocorreu alteracao
        # Grava configuração anterior
        # concept_preferred_term_old
        # Decide prenchimento com [ 01, 02, 03, 04 ou 16 ] ou [ 51, 52, 53, 54 e 516]
        if concept_preferred_term_old == 'Y':
            if language_code == 'en':
                sub_t='01'
            if language_code == 'es':
                sub_t='02'
            if language_code == 'pt-br':
                sub_t='03'
            if language_code == 'es-es':
                sub_t='04'
            if language_code == 'fr':
                sub_t='16'
        else:
            if language_code == 'en':
                sub_t='51'
            if language_code == 'es':
                sub_t='52'
            if language_code == 'pt-br':
                sub_t='53'
            if language_code == 'es-es':
                sub_t='54'
            if language_code == 'fr':
                sub_t='516'
        term_string_historical = v998 + sub_t

        if concept_preferred_term == 'Y' and record_preferred_term == 'Y':

            # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
            # Search by published record
            q_status_published = Q(
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                concept_preferred_term="Y",
                                record_preferred_term="Y",
                                identifier_concept_id=identifier_concept_id,
                                # status=1,
                                )

        if concept_preferred_term == 'Y' and record_preferred_term == 'N':

            # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "N"
            # Search by published record
            q_status_published = Q(
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                concept_preferred_term="Y",
                                record_preferred_term="N",
                                identifier_concept_id=identifier_concept_id,
                                # status=1,
                                )
        # Avalia conceito PREFERIDO
        if ( concept_preferred_term == 'Y' and record_preferred_term == 'Y' ) or ( concept_preferred_term == 'Y' and record_preferred_term == 'N' ):

            has_term_config = TermListDesc.objects.filter( q_status_published ).values('id').exclude(id=self.object.id,)

            if len(has_term_config) > 0:

                msg_erro =  _("This configuration already exists for this concept!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                                    form=form,
                                                                    formset_toccurrence=formset_toccurrence,
                                                                    msg_erro=msg_erro,
                                                                    ))
            else:

                # Search by draft record
                q_status_draft = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=-1,
                                    )

                # Search by published record
                q_status_published = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=1,
                                    )

                # Search by historical record
                q_status_historical = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=5,
                                    )

                has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).exclude(id=self.object.id).values('term_string')

                # Corre resultados e compara
                has_equal=''
                for term in has_term:
                    t=term.get('term_string').encode('utf-8')
                    if t == term_string.encode('utf-8'):
                        # print 'Igual-->',t
                        has_equal=t

                if has_equal:
                    msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        formset_toccurrence=formset_toccurrence,
                                                                        msg_erro=msg_erro,
                                                                        ))
                else:

                    # Se não existe configuração para o termo e não existe um termo igual pode prosseguir com a atualização.
                    form_valid = form.is_valid()
                    formset_toccurrence_valid = formset_toccurrence.is_valid()

                    if (form_valid and formset_toccurrence_valid):

                        self.object = form.save(commit=False)

                        self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                        self.object.date_altered = datetime.datetime.now().strftime('%Y-%m-%d')

                        if len(historical_annotation_old) > 0:
                            term_string_historical=term_string_historical + ';' + historical_annotation_old

                        self.object.historical_annotation = term_string_historical

                        self.object = form.save(commit=True)

                        formset_toccurrence.instance = self.object
                        formset_toccurrence.save()

                        form.save()
                        return HttpResponseRedirect(self.get_success_url())

                    else:
                        return self.render_to_response(self.get_context_data(
                                                                            form=form,
                                                                            formset_toccurrence=formset_toccurrence,
                                                                            ))
        else:
        
            # Avalia conceito NÃO PREFERIDO

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=5,
                                )

            has_term = TermListDesc.objects.filter( q_status_draft | q_status_published | q_status_historical ).exclude(id=self.object.id).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_string.encode('utf-8'):
                    # print 'Igual-->',t
                    has_equal=t

            if has_equal:
                msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                                    form=form,
                                                                    formset_toccurrence=formset_toccurrence,
                                                                    msg_erro=msg_erro,
                                                                    ))
            else:
                form_valid = form.is_valid()
                formset_toccurrence_valid = formset_toccurrence.is_valid()

                if (form_valid and formset_toccurrence_valid):

                    self.object = form.save(commit=False)

                    self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                    self.object.date_altered = datetime.datetime.now().strftime('%Y-%m-%d')

                    term_string_historical = v998 + sub_t

                    if len(historical_annotation_old) > 0:
                        term_string_historical=term_string_historical + ';' + historical_annotation_old

                    self.object.historical_annotation = term_string_historical

                    self.object = form.save(commit=True)

                    formset_toccurrence.instance = self.object
                    formset_toccurrence.save()

                    form.save()
                    return HttpResponseRedirect(self.get_success_url())

                else:
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        formset_toccurrence=formset_toccurrence,
                                                                        ))

    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( self.object.id, ths )


    def get_context_data(self, **kwargs):
        context = super(TermListDescUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.POST:
            context['formset_toccurrence'] = TheraurusOccurrenceListDescFormSet(self.request.POST)
        else:
            context['formset_toccurrence'] = TheraurusOccurrenceListDescFormSet(instance=self.object)
        return context



class legacyInformationDescCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create legacy information
    """
    model = legacyInformationDesc
    template_name = 'thesaurus/descriptor_new_legacy.html'
    form_class = legacyInformationDescForm

    def get_success_url(self):

        id_identifier = self.request.GET.get("identifier_id")

        # Search ID of the first concept of this record
        concepts_of_registry = IdentifierConceptListDesc.objects.filter(identifier_id=id_identifier).values('id')
        id_concept = concepts_of_registry[0].get('id')

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListDesc.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( id_term, ths )

    def form_valid(self, form):

        if form.is_valid():

            self.object = form.save(commit=False)
            self.object.identifier_id = self.request.POST.get("identifier_id")
            self.object = form.save()
            form.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(legacyInformationDescCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context



class legacyInformationDescUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update a legacy information
    """
    model = legacyInformationDesc
    template_name = 'thesaurus/descriptor_edit_legacy.html'
    form_class = legacyInformationDescForm


    def get_success_url(self):

        id_identifier = self.request.GET.get("identifier_id")

        # Search ID of the first concept of this record
        concepts_of_registry = IdentifierConceptListDesc.objects.filter(identifier_id=id_identifier).values('id')
        id_concept = concepts_of_registry[0].get('id')

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListDesc.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/descriptors/view/%s%s' % ( id_term, ths )

    def form_valid(self, form):

        if form.is_valid():

            self.object = form.save()
            form.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(legacyInformationDescUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context




class PageViewDesc(LoginRequiredView, DetailView):
    """
    Used as class DetailView to list the result
    """
    model = TermListDesc
    template_name = 'thesaurus/page_view_desc.html'

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(PageViewDesc, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        lang_code = get_language()

        context = super(PageViewDesc, self).get_context_data(**kwargs)

        if self.object:

            # IdentifierConceptListDesc - recover pk from concept
            id_concept = IdentifierConceptListDesc.objects.filter(
                                            id=self.object.identifier_concept_id,
                                            ).values('identifier_id').distinct()

            # Usado para criar novo conceito
            for concept in id_concept:
                context['id_concept_new'] = concept


            # IdentifierConceptListDesc - retrieves pk's that has even identifier_id - can bring more than 1
            ids = IdentifierConceptListDesc.objects.filter(
                                            identifier_id=id_concept,
                                            ).values('id')

            # IdentifierDesc
            # Brings information to Active Descriptor Record
            context['identifierdesc_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            )

            # IdentifierDesc
            context['id_register_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(

                                                # IdentifierDesc
                                                'id',
                                                'thesaurus',
                                                'descriptor_class',
                                                'descriptor_ui',
                                                'decs_code',
                                                'external_code',
                                                'nlm_class_number',
                                                'date_created',
                                                'date_revised',
                                                'date_established',
                                                'abbreviation',
                                            )

            context['description_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # DescriptionDesc
                                                'descriptiondesc__identifier_id',
                                                'descriptiondesc__language_code',
                                                'descriptiondesc__annotation',
                                                'descriptiondesc__history_note',
                                                'descriptiondesc__online_note',
                                                'descriptiondesc__public_mesh_note',
                                                'descriptiondesc__consider_also',
                                            )

            # Usado para criar lista de Indexacao Previa
            context['previous_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # PreviousIndexingListDesc
                                                'previousdesc__identifier_id',
                                                'previousdesc__previous_indexing',
                                                'previousdesc__language_code',
                                            ).distinct().order_by('previousdesc__previous_indexing')

            # Usado para criar lista de Acao farmacologica
            context['pharmaco_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # PharmacologicalActionList
                                                'pharmacodesc__identifier_id',
                                                'pharmacodesc__term_string',
                                                'pharmacodesc__descriptor_ui',
                                                'pharmacodesc__language_code',
                                            ).distinct().order_by('pharmacodesc__term_string')

            # Usado para criar lista de tree number
            context['tree_numbers_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # TreeNumbersListDesc
                                                'dtreenumbers__identifier_id',
                                                'dtreenumbers__tree_number',
                                            ).distinct().order_by('dtreenumbers__tree_number')

            # Usado para criar lista de See Also - related
            context['related_objects'] = IdentifierDesc.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # TreeNumbersListDesc
                                                'relateddesc__term_string',
                                                'relateddesc__descriptor_ui',
                                            ).distinct().order_by('relateddesc__term_string')

            context['term_string_info_preferred_objects'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,termdesc__concept_preferred_term='Y',termdesc__record_preferred_term='Y',
                                            ).order_by('identifier_id',
                                                        'termdesc__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termdesc__concept_preferred_term',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'id',
                                                    'termdesc__status',
                                                    'termdesc__term_string',
                                                    'termdesc__language_code',
                                                    'identifier_id',
                                            )

            context['entry_terms_objects'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,termdesc__status=1,termdesc__record_preferred_term='N',
                                            ).order_by('identifier_id',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'id',
                                                    'termdesc__id',
                                                    'termdesc__term_string',
                                                    'termdesc__language_code',
                                            )

            context['scope_note_objects'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by('identifier_id',
                                            ).values(
                                                    'conceptdesc__language_code',
                                                    'conceptdesc__scope_note',
                                            ).distinct()

            context['legacy_objects'] = legacyInformationDesc.objects.filter(
                                            identifier=id_concept,
                                            ).values(
                                                'id',
                                                'pre_codificado',
                                                'desastre',
                                                'reforma_saude',
                                                'geografico',
                                                'mesh',
                                                'pt_lilacs',
                                                'nao_indexavel',
                                                'homeopatia',
                                                'repidisca',
                                                'saude_publica',
                                                'exploded',
                                                'geog_decs',
                                                'identifier_id',
                                            )

            context['entrycombination_objects'] = EntryCombinationListDesc.objects.filter(
                                            identifier=id_concept,
                                            ).values(
                                                'id',
                                                'ecin_qualif',
                                                'ecin_id',
                                                'ecout_desc',
                                                'ecout_desc_id',
                                                'ecout_qualif',
                                                'ecout_qualif_id',
                                                'identifier_id',
                                            )


            # Usado para mostrar informações de conceitos e termos Preferidos
            context['identifierconceptlist_objects_preferred'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by(
                                                        '-preferred_concept',
                                                        '-termdesc__concept_preferred_term',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'id',
                                                    'identifier_id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',
                                                    'casn1_name',
                                                    'registry_number',

                                                    'conceptdesc__identifier_concept_id',
                                                    'conceptdesc__language_code',
                                                    'conceptdesc__scope_note',

                                                    'termdesc__id',
                                                    'termdesc__identifier_concept_id',
                                                    'termdesc__status',
                                                    'termdesc__term_ui',
                                                    'termdesc__language_code',
                                                    'termdesc__term_string',
                                                    'termdesc__concept_preferred_term',
                                                    'termdesc__is_permuted_term',
                                                    'termdesc__lexical_tag',
                                                    'termdesc__record_preferred_term',
                                                    'termdesc__entry_version',
                                                    'termdesc__date_created',
                                                    'termdesc__date_altered',
                                                    'termdesc__historical_annotation',
                                            ).distinct()

            # Usado para mostrar informações de conceitos e termos Preferidos para Aba de Conceitos
            context['identifierconceptlist_objects_preferred_for_concepts'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by(
                                                        '-preferred_concept',
                                                        '-termdesc__concept_preferred_term',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'identifier_id',
                                                    'id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',


                                                    'termdesc__id',
                                                    'termdesc__identifier_concept_id',
                                                    'termdesc__status',
                                                    'termdesc__term_ui',
                                                    'termdesc__language_code',
                                                    'termdesc__term_string',
                                                    'termdesc__concept_preferred_term',
                                                    'termdesc__is_permuted_term',
                                                    'termdesc__lexical_tag',
                                                    'termdesc__record_preferred_term',
                                                    'termdesc__entry_version',
                                                    'termdesc__date_created',
                                                    'termdesc__date_altered',
                                                    'termdesc__historical_annotation',
                                            ).distinct()


            # Usado para mostrar informações de conceitos e termos Não Preferidos 
            context['identifierconceptlist_objects'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,preferred_concept='N',
                                            ).order_by('identifier_id',
                                                        'termdesc__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termdesc__concept_preferred_term',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'id',
                                                    'identifier_id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',
                                                    'casn1_name',
                                                    'registry_number',

                                                    'conceptdesc__identifier_concept_id',
                                                    'conceptdesc__language_code',
                                                    'conceptdesc__scope_note',

                                                    'termdesc__id',
                                                    'termdesc__identifier_concept_id',
                                                    'termdesc__status',
                                                    'termdesc__term_ui',
                                                    'termdesc__language_code',
                                                    'termdesc__term_string',
                                                    'termdesc__concept_preferred_term',
                                                    'termdesc__is_permuted_term',
                                                    'termdesc__lexical_tag',
                                                    'termdesc__record_preferred_term',
                                                    'termdesc__entry_version',
                                                    'termdesc__date_created',
                                                    'termdesc__date_altered',
                                                    'termdesc__historical_annotation',
                                            ).distinct()

            # Usado para mostrar informações de conceitos e termos Não Preferidos para Aba Conceitos
            context['identifierconceptlist_objects_for_concepts'] = IdentifierConceptListDesc.objects.filter(
                                            identifier=id_concept,preferred_concept='N',
                                            ).order_by('identifier_id',
                                                        'termdesc__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termdesc__concept_preferred_term',
                                                        'termdesc__language_code',
                                                        'termdesc__term_string',
                                            ).values(
                                                    'identifier_id',
                                                    'id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',

                                                    'termdesc__id',
                                                    'termdesc__identifier_concept_id',
                                                    'termdesc__status',
                                                    'termdesc__term_ui',
                                                    'termdesc__language_code',
                                                    'termdesc__term_string',
                                                    'termdesc__concept_preferred_term',
                                                    'termdesc__is_permuted_term',
                                                    'termdesc__lexical_tag',
                                                    'termdesc__record_preferred_term',
                                                    'termdesc__entry_version',
                                                    'termdesc__date_created',
                                                    'termdesc__date_altered',
                                                    'termdesc__historical_annotation',
                                            ).distinct()




            # Traz abbreviation e term_string do idioma da interface no momento
            id_abbrev = IdentifierDesc.objects.filter(id=id_concept).values('abbreviation')
            translation = IdentifierQualif.objects.filter(id__in=id_abbrev).order_by('abbreviation') # Usado __in pois pode haver mais que um resultado
            
            context['allowable_qualifiers_objects'] = translation

            # Informacoes para log
            # Registro
            # ID do model
            id_ctype_identifierdesc = ContentType.objects.filter(model='identifierdesc').values('id')
            context['id_ctype_identifierdesc'] = id_ctype_identifierdesc[0].get('id')
            # ID do registro
            id_identifierdesc = IdentifierDesc.objects.filter(id=id_concept).values('id')
            context['id_identifierdesc'] = id_identifierdesc[0].get('id')

            # # Concept e Term
            # id_ctype_identifierdesc = ContentType.objects.filter(model='identifierdesc').values('id')
            # context['id_ctype_identifierdesc'] = id_ctype_identifierdesc[0].get('id')
            # # ID do registro
            # id_identifierdesc = IdentifierDesc.objects.filter(id=id_concept).values('id')
            # context['id_identifierdesc'] = id_identifierdesc[0].get('id')

            context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

            return context




# Qualifiers -------------------------------------------------------------------------
class QualifUpdate(LoginRequiredView):
    """
    Handle creation and update of Qualifiers objects
    """
    model = IdentifierQualif
    # success_url = reverse_lazy('list_descriptor')
    success_url = reverse_lazy('create_concept_termqualif')

    
    form_class = IdentifierQualifForm
    template_name = "thesaurus/qualifier_form_step1.html"

    def form_valid(self, form):

        formset_descriptor = DescriptionQualifFormSet(self.request.POST, instance=self.object)
        formset_treenumber = TreeNumbersListQualifFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_treenumber_valid = formset_treenumber.is_valid()

        if (form_valid and 
            formset_descriptor_valid and 
            formset_treenumber_valid
            ):
            # self.object = form.save()

            # Verifica se foi passado algum valor para formset_treenumber
            tree_number_existentes=''
            exist_tree_numbers=0
            for f in formset_treenumber:
                if f.cleaned_data is not None:
                    fields_t = f.cleaned_data
                    content_tree_number = fields_t.get('tree_number')

                    # Essa variável é do cleaned_data e diz se o registro foi apagado ou não no formulário
                    # Se for True foi apagado
                    status_preenchimento = fields_t.get('DELETE')

                    if status_preenchimento == False:
                        exist_tree_numbers = exist_tree_numbers + 1

                        # Verifica se ja existe cadastrado o tree_number para este tesauro
                        result_tree_number = TreeNumbersListQualif.objects.filter(tree_number=content_tree_number).values('identifier_id')

                        if result_tree_number is not None:
                            for t in result_tree_number:
                                identifier_id_existent_tree_number = t.get('identifier_id')

                                # Checks if the record is for the thesaurus being worked on
                                res_existent_thesaurus_id = IdentifierQualif.objects.filter(id=identifier_id_existent_tree_number).values('thesaurus_id')
                                existent_thesaurus_id=res_existent_thesaurus_id[0].get('thesaurus_id')

                                # Brings id of thesaurus currently operating
                                environment_thesaurus_id = self.request.GET.get("ths")

                                # If tree_number exists in same thesaurus creates error
                                if int(environment_thesaurus_id) == int(existent_thesaurus_id):
                                    tree_number_existentes = tree_number_existentes + content_tree_number + '   '

            # Condição para poder criar registro
            if not tree_number_existentes and exist_tree_numbers > 0:

                # Bring the choiced language_code from the first form
                # registry_language = formset_descriptor.cleaned_data[0].get('language_code')
                registry_language = self.request.GET.get("language_code")

                # Get sequential number to write to decs_code
                self.object = form.save(commit=False)
                ths = self.request.GET.get("ths")
                try:
                    seq = code_controller.objects.get(thesaurus=self.request.GET.get("ths"))
                    nseq = str(int(seq.sequential_number) + 1)
                    seq.sequential_number = nseq
                    seq.save()
                except code_controller.DoesNotExist:
                    seq = code_controller(sequential_number=1,thesaurus=ths)
                    nseq = 1
                    seq.save()
                self.object.decs_code = nseq
                self.object = form.save(commit=True)

                # Get thesaurus_acronym to create new ID format to descriptor_ui field
                self.object = form.save(commit=False)
                try:
                    acronym = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_acronym')
                    # recupera o acronimo e transforma em maiusuclo
                    acronym = str(acronym[0].get('thesaurus_acronym')).upper()
                    # utiliza self.object.decs_code para compor qualifier_ui
                    zseq = str(self.object.decs_code).zfill(6) # preenche zeros a esquerda
                    self.object.qualifier_ui = 'Q' + acronym + zseq
                except Thesaurus.DoesNotExist:
                    id_thesaurus = str(self.object.id)
                    print 'Warning! - No thesaurus_acronym for id -->',id_thesaurus
                self.object = form.save(commit=True)

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_treenumber.instance = self.object
                formset_treenumber.save()

                form.save()

                # Essas variaveis dizem respeito a criação de novo registro a partir de um termo existente
                # Quando existirem serão repassadas para a faze de criação de conceito
                if self.request.GET.get("term_ui") and self.request.GET.get("term_id"):

                    term_ui_alter = self.request.GET.get("term_ui")
                    term_id_alter = self.request.GET.get("term_id")
                    return redirect(reverse('create_concept_termqualif') + '?ths=' + self.request.GET.get("ths") + '&' + 'registry_language=' + registry_language + '&term=' + self.request.GET.get("term") + '&term_ui_alter=' + term_ui_alter + '&term_id_alter=' + term_id_alter)
                else:
                    return redirect(reverse('create_concept_termqualif') + '?ths=' + self.request.GET.get("ths") + '&' + 'registry_language=' + registry_language + '&term=' + self.request.GET.get("term"))

            else:
                if exist_tree_numbers == 0:
                    msg_erro = _("Hierarchical level")
                else:
                    msg_erro = _("already exists!!!") + ' -----> ' + tree_number_existentes
                return self.render_to_response(
                            self.get_context_data(
                                                form=form,
                                                formset_descriptor=formset_descriptor,
                                                formset_treenumber=formset_treenumber,
                                                msg_erro=msg_erro,
                                                )
                                            )
        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_treenumber=formset_treenumber,
                                            )
                                        )

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(QualifUpdate, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['language_system'] = get_language()

        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionQualifFormSet(instance=self.object)
            context['formset_treenumber'] = TreeNumbersListQualifFormSet(instance=self.object)
      
        return context


class QualifCreateView(QualifUpdate, CreateView):
    """
    Used as class view to create Qualifiers
    """
    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(QualifCreateView, self).dispatch(*args, **kwargs)



class QualifDeleteView(QualifUpdate, DeleteView):
    """
    Used as class view to delete Qualifier
    """
    model = IdentifierQualif
    template_name = 'thesaurus/qualifier_confirm_delete.html'

    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/%s' % ths 



class QualifListDescChk(LoginRequiredView, ListView):
    """
    Used to verify if already exist the term
    """
    template_name = "thesaurus/qualifier_form_step0.html"
    context_object_name = "registers"

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")
            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(QualifListDescChk, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        return object_list


    def get_context_data(self, **kwargs):
        context = super(QualifListDescChk, self).get_context_data(**kwargs)

        context['choiced_thesaurus_info'] = Thesaurus.objects.filter(id=self.request.GET.get("thesaurus"))

        context['term_choiced'] = self.actions['term_string']
        context['filter_language'] = self.actions['filter_language']

        return context


    def render_to_response(self, context):
        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['term_string'] and self.actions['filter_language']:

            term_choiced = self.actions['term_string']

            # Para poder criar um termo novo, não deve existir
            # -1 - Rascunho
            # 1  - Publicado
            # 5  - Histórico

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=self.actions['term_string'],
                                language_code=self.actions['filter_language'],
                                term_thesaurus=self.request.GET.get("thesaurus"),
                                status=5,
                                )

            has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_choiced.encode('utf-8'):
                    # print 'Igual-->',t,'   -   ',term_choiced.encode('utf-8')
                    has_equal=t            

            if not has_equal:
                return redirect('/thesaurus/qualifiers/new/?ths=' + self.request.GET.get("thesaurus") + '&term=' + self.actions['term_string'] + '&language_code=' + self.actions['filter_language'])

        return super(QualifListDescChk, self).render_to_response(context)



class QualifRegisterUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update a register of qualifier
    """
    model = IdentifierQualif
    template_name = 'thesaurus/qualifier_edit_register.html'
    form_class = IdentifierQualifForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(QualifRegisterUpdateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):

        id_register = self.object.id

        # Search ID of the first concept of the record to later search the first term of the concept
        concepts_of_register = IdentifierConceptListQualif.objects.filter(identifier_id=id_register).values('id')
        id_concept = concepts_of_register[0].get('id')

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( id_term, ths )


    def form_valid(self, form):

        formset_descriptor = DescriptionQualifFormSet(self.request.POST, instance=self.object)
        formset_treenumber = TreeNumbersListQualifFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_treenumber_valid = formset_treenumber.is_valid()

        if (form_valid and 
            formset_descriptor_valid and 
            formset_treenumber_valid
            ):


            # Verifica se foi passado algum valor para formset_treenumber
            tree_number_existentes=''
            # Utilizado para verificar se o form está totalmente vazio - o que não deve ocorrer
            form_vazio=True
            exist_tree_numbers=0
            for f in formset_treenumber:
                if f.cleaned_data is not None:
                    fields_t = f.cleaned_data
                    content_tree_number = fields_t.get('tree_number')

                    identifier_id = fields_t.get('identifier')
                    # Onde identifier_id = 'identifier': <IdentifierDesc: 34244>
                    # Exemplo
                    # ---> {'identifier': <IdentifierDesc: 34244>, 'tree_number': u'SP4.026.307.808.100', u'id': <TreeNumbersListDesc: 68760>, u'DELETE': False}
                    # Para utilizar referenciar identifier_id.id

                    # Essa variável é do cleaned_data e diz se o registro foi apagado ou não no formulário
                    # Se for True foi apagado
                    status_preenchimento = fields_t.get('DELETE')

                    if status_preenchimento == False:
                        form_vazio=False
                        exist_tree_numbers = exist_tree_numbers + 1

                        # Verifica se ja existe cadastrado o tree_number para este tesauro
                        result_tree_number = TreeNumbersListQualif.objects.filter(tree_number=content_tree_number).exclude(identifier_id=identifier_id.id).values('identifier_id')

                        if result_tree_number is not None:
                            for t in result_tree_number:
                                identifier_id_existent_tree_number = t.get('identifier_id')

                                # Checks if the record is for the thesaurus being worked on
                                res_existent_thesaurus_id = IdentifierQualif.objects.filter(id=identifier_id_existent_tree_number).values('thesaurus_id')
                                existent_thesaurus_id=res_existent_thesaurus_id[0].get('thesaurus_id')

                                # Brings id of thesaurus currently operating
                                environment_thesaurus_id = self.request.GET.get("ths")

                                # If tree_number exists in same thesaurus creates error
                                if int(environment_thesaurus_id) == int(existent_thesaurus_id):
                                    tree_number_existentes = tree_number_existentes + content_tree_number + '   '

            # Condição para poder criar registro
            if not tree_number_existentes and exist_tree_numbers > 0 and form_vazio==False:

                # Bring the choiced language_code from the first form
                registry_language = formset_descriptor.cleaned_data[0].get('language_code')

                self.object = form.save()

                formset_descriptor.instance = self.object
                formset_descriptor.save()

                formset_treenumber.instance = self.object
                formset_treenumber.save()

                form.save()

                return HttpResponseRedirect(self.get_success_url())

            else:
                if form_vazio == True:
                    ths = self.request.GET.get("ths")
                    return redirect('/thesaurus/qualifiers?ths=' + ths)

                elif exist_tree_numbers == 0:
                    msg_erro = _("Hierarchical level")
                else:
                    msg_erro = _("already exists!!!") + ' -----> ' + tree_number_existentes
                return self.render_to_response(
                            self.get_context_data(
                                                form=form,
                                                formset_descriptor=formset_descriptor,
                                                formset_treenumber=formset_treenumber,
                                                msg_erro=msg_erro,
                                                )
                                            )
        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_treenumber=formset_treenumber,
                                            )
                                        )

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(QualifRegisterUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['language_system'] = get_language()

        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionQualifFormSet(instance=self.object)
            context['formset_treenumber'] = TreeNumbersListQualifFormSet(instance=self.object)
      
        return context



class QualifListView(LoginRequiredView, ListView):
    """
    List qualifier records
    """
    template_name = "thesaurus/qualifier_list.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE


    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            elif self.request.GET.get("ths"):
                environment_thesaurus_id=self.request.GET.get("ths")
            elif self.request.POST.get("choiced_thesaurus"):
                environment_thesaurus_id=self.request.POST.get("choiced_thesaurus")
            else:
                self.actions = {}
                for key in ACTIONS.keys():
                    self.actions[key] = self.request.GET.get(key, ACTIONS[key])
                environment_thesaurus_id=self.actions['choiced_thesaurus']

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(QualifListView, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        lang_code = get_language()
        object_list = []
        registers_indexed = []
        concepts_indexed = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        # icontains X exact -------------------------------------------------------------------------------------
        if self.actions['exact']:
            q_term_string = Q(term_string=self.actions['s'])
        else:
            q_term_string = Q(term_string__icontains=self.actions['s'])

        # term_string
        if self.actions['filter_fields'] == 'term_string' and self.actions['exact']:
            q_term_string = Q(term_string=self.actions['s'])
        else:
            if self.actions['filter_fields'] == 'term_string' and not self.actions['exact']:
                q_term_string = Q(term_string__icontains=self.actions['s'])

        # concept_preferred_term='Y'
        q_concept_preferred_term = Q(concept_preferred_term='Y')

        # record_preferred_term='Y'
        q_record_preferred_term = Q(record_preferred_term='Y')

        # status
        if self.actions['filter_status']:
            q_filter_status = Q(status=self.actions['filter_status'])


        # Term
        # AND performance for Term ------------------------------------------------------------------------
        # Do the initial search in term_string field
        if self.actions['s'] and not self.actions['filter_fields']:
            object_list = TermListQualif.objects.filter( q_term_string ).filter(term_thesaurus=self.actions['choiced_thesaurus']).exclude(status=-3).order_by('term_string')
        else:
            # bring all registers
            object_list = TermListQualif.objects.all().filter(term_thesaurus=self.actions['choiced_thesaurus']).exclude(status=-3).order_by('term_string')

        # term_string
        if self.actions['filter_fields'] == 'term_string' and self.actions['s']:
            object_list = TermListQualif.objects.filter( q_term_string ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # Concept
        # AND performance for Concept ------------------------------------------------------------------------
        # when concept_preferred_term='Y' & record_preferred_term='Y'
        if self.actions['filter_fields'] == 'concept':
            object_list = TermListQualif.objects.filter( q_term_string & q_concept_preferred_term & q_record_preferred_term ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # Abbreviation
        # AND performance for Abbreviation --------------------------------------------------------------
        if self.actions['filter_fields'] == 'abbreviation':
            id_register = IdentifierQualif.objects.filter(abbreviation=self.actions['s']).values('id')
            id_concept = IdentifierConceptListQualif.objects.filter(identifier_id=id_register,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListQualif.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])



        # MESH Qualifier UI
        # AND performance for MESH Qualifier UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'qualifier_ui':
            id_register = IdentifierQualif.objects.filter(qualifier_ui=self.actions['s']).values('id')
            id_concept = IdentifierConceptListQualif.objects.filter(identifier_id=id_register,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListQualif.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])



        # DeCS Qualifier UI
        # AND performance for DeCS Qualifier UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'decs_code':
            id_register = IdentifierQualif.objects.filter(decs_code=self.actions['s']).values('id')
            id_concept = IdentifierConceptListQualif.objects.filter(identifier_id=id_register,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListQualif.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # Tree Number
        # AND performance for Tree Number --------------------------------------------------------------
        if self.actions['filter_fields'] == 'tree_number':
            id_tree_number = TreeNumbersListQualif.objects.filter(tree_number=self.actions['s']).values('identifier_id')
            id_concept = IdentifierConceptListQualif.objects.filter(identifier_id__in=id_tree_number,preferred_concept='Y').distinct().values('id')
            q_id_concept = Q(identifier_concept_id__in=id_concept)
            object_list = TermListQualif.objects.filter( q_concept_preferred_term & q_record_preferred_term & q_id_concept ).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')

        # Concept UI
        # AND performance for Concept UI --------------------------------------------------------------
        if self.actions['filter_fields'] == 'concept_ui':
            concept_identifier_id = IdentifierConceptListQualif.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
            id_register = IdentifierQualif.objects.filter(id__in=concept_identifier_id,thesaurus_id=self.actions['choiced_thesaurus']).values('id')
            concept_id = IdentifierConceptListQualif.objects.filter(identifier_id=id_register,concept_ui=self.actions['s']).values('id')
            object_list = TermListQualif.objects.filter(identifier_concept_id=concept_id).filter(term_thesaurus=self.actions['choiced_thesaurus']).order_by('term_string')


        # status
        if self.actions['filter_status']:
            object_list = object_list.filter(status=self.actions['filter_status'])

        # language
        if self.actions['filter_language']:
            object_list = object_list.filter(language_code=self.actions['filter_language'])


        # order performance -------------------------------------------------------------------------------------
        if self.actions['order'] == "-":
            object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

        # if self.actions['visited'] != 'ok':
        #     object_list = object_list.none()

        return object_list



    def get_context_data(self, **kwargs):
        context = super(QualifListView, self).get_context_data(**kwargs)

        context['actions'] = self.actions

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))
        context['last_created_objects_list'] = TermListQualif.objects.filter(term_thesaurus=self.request.GET.get("ths")).exclude(status=-3).exclude(status=3).exclude(status=5).exclude(date_created__isnull=True).order_by('-date_created','-id')[:10][::-1]
        context['last_altered_objects_list'] = TermListQualif.objects.filter(term_thesaurus=self.request.GET.get("ths")).exclude(status=-3).exclude(date_altered__isnull=True).order_by('-date_altered','-id')[:10][::-1]

        return context







# FORM 2
# Cria conceito e termo
class QualifConceptTermUpdate(LoginRequiredView):
    """
    Used as class view to create ConceptTermUpdate
    """
    model = IdentifierConceptListQualif
    form_class = IdentifierConceptListQualifForm
    template_name = 'thesaurus/qualifier_form_step2.html'

    def form_valid(self, form):

        formset_concept = ConceptListQualifFormSet(self.request.POST, instance=self.object)
        formset_term = TermListQualifFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_concept_valid and formset_term_valid):
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("termqualif-0-term_string")
            language_code = self.request.POST.get("termqualif-0-language_code")
            term_thesaurus = self.request.GET.get("ths")

            # Se existirem essas variaveis não deverá ser realizado a verificação de existência pois nesse caso 
            # será forçado a criação de novo registro, e o registro antigo será alterado seu status
            if self.request.GET.get("term_ui_alter") and self.request.GET.get("term_id_alter"):

                self.object = form.save()

                # Get thesaurus_acronym to create new ID format to concept_ui field
                self.object = form.save(commit=False)
                zseq = str(self.object.id).zfill(8) # preenche zeros a esquerda
                self.object.concept_ui = 'FQ' + zseq
                self.object = form.save(commit=True)

                formset_concept.instance = self.object
                formset_concept.save()

                formset_term.instance = self.object
                formset_term.save()

                # Bring the choiced language_code from the first form
                registry_language = formset_term.cleaned_data[0].get('language_code')

                # Update the created term_ui with a old content - term_ui_alter
                try:
                    created_id = int(TermListQualif.objects.latest('id').id)
                    update_field = TermListQualif.objects.get(id=created_id)
                    update_field.term_ui = self.request.GET.get("term_ui_alter")

                    # descobre id do conceito que o termo antigo pertence
                    identifier_concept_id = TermListQualif.objects.filter(id=self.request.GET.get("term_id_alter")).values('identifier_concept_id')
                    identifier_concept_id = identifier_concept_id[0].get('identifier_concept_id')

                    # descobre concept_ui
                    concept_ui_origem = IdentifierConceptListQualif.objects.filter(id=identifier_concept_id).values('concept_ui')
                    concept_ui_origem = concept_ui_origem[0].get('concept_ui')

                    # coleta informação do histórico do term antigo
                    historical_annotation_old=TermListQualif.objects.filter(id=self.request.GET.get("term_id_alter")).values('historical_annotation')
                    if len(historical_annotation_old) > 0:
                        historical_annotation_old=historical_annotation_old[0].get('historical_annotation')
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
                    else:
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8')

                    update_field.historical_annotation = historical_annotation_new

                    update_field.save()

                except TermListQualif.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                # Update old term register, status and historical_annotation - term_id_alter
                try:
                    # Busca informação do concept_ui do novo termo
                    created_id = int(TermListQualif.objects.latest('id').id)

                    # descobre id do conceito que o termo antigo pertence
                    identifier_concept_id = TermListQualif.objects.filter(id=created_id).values('identifier_concept_id')
                    identifier_concept_id = identifier_concept_id[0].get('identifier_concept_id')

                    # descobre concept_ui
                    concept_ui_destino = IdentifierConceptListQualif.objects.filter(id=identifier_concept_id).values('concept_ui')
                    concept_ui_destino = concept_ui_destino[0].get('concept_ui')

                    # coleta informação do histórico do term antigo
                    historical_annotation_old=TermListQualif.objects.filter(id=self.request.GET.get("term_id_alter")).values('historical_annotation')
                    if len(historical_annotation_old) > 0:
                        historical_annotation_old=historical_annotation_old[0].get('historical_annotation')
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - sent to ' + concept_ui_destino
                        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
                    else:
                        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - sent to ' + concept_ui_origem
                        historical_annotation_new=historical_annotation_now.encode('utf-8')

                    update_field = TermListQualif.objects.get(id=self.request.GET.get("term_id_alter"))
                    update_field.status = '-3'
                    update_field.historical_annotation = historical_annotation_new

                    update_field.save()
                except TermListQualif.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                form.save()

                return HttpResponseRedirect(self.get_success_url())

            else:
                has_term = TermListQualif.objects.filter(
                    term_string__exact=term_string,
                    language_code=language_code,
                    term_thesaurus=term_thesaurus,
                    status=1,
                    ).exists()

                if not has_term:
                    self.object = form.save()

                    # Get thesaurus_acronym to create new ID format to concept_ui field
                    self.object = form.save(commit=False)
                    zseq = str(self.object.id).zfill(8) # preenche zeros a esquerda
                    self.object.concept_ui = 'FQ' + zseq
                    self.object = form.save(commit=True)

                    formset_concept.instance = self.object
                    formset_concept.save()

                    formset_term.instance = self.object
                    formset_term.save()

                    # Bring the choiced language_code from the first form
                    registry_language = formset_term.cleaned_data[0].get('language_code')

                    # Get thesaurus_acronym to create new ID format to term_ui field
                    try:
                        acronym = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_acronym')
                        acronym = acronym[0].get('thesaurus_acronym')
                    except Thesaurus.DoesNotExist:
                        id_thesaurus = str(self.object.id)
                        print 'Warning! - No thesaurus_acronym for id -->',id_thesaurus
                        acronym = ''

                    # Update term_ui with a new format
                    try:

                        ths = self.request.GET.get("ths")
                        try:
                            seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                            nseq = str(int(seq.sequential_number) + 1)
                            seq.sequential_number = nseq
                            seq.save()
                        except code_controller_term.DoesNotExist:
                            seq = code_controller_term(sequential_number=1,thesaurus=ths)
                            nseq = 1
                            seq.save()
                        created_id = int(TermListQualif.objects.latest('id').id)
                        update_field = TermListQualif.objects.get(id=created_id)

                        # substitui idioma do sistema por sigla de 3 letras
                        if registry_language == 'en':
                            language_3letters = 'eng'
                        if registry_language == 'es':
                            language_3letters = 'spa'
                        if registry_language == 'pt-br':
                            language_3letters = 'por'
                        if registry_language == 'fr':
                            language_3letters = 'fre'
                        if registry_language == 'es-es':
                            language_3letters = 'spa'

                        # preenche zeros a esquerda
                        zseq = str(nseq).zfill(6)

                        update_field.term_ui = language_3letters + 'q' + zseq
                        update_field.save()
                    except TermListQualif.DoesNotExist:
                        print 'Warning! Does not exist id to this Term'

                    form.save()

                    return HttpResponseRedirect(self.get_success_url())
                else:
                    msg_erro =  _("This Concept already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                    form=form,
                                                    formset_concept=formset_concept,
                                                    formset_term=formset_term,
                                                    msg_erro=msg_erro,
                                                    ))
        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_concept=formset_concept,
                                            formset_term=formset_term,
                                            )
                                        )

    def get_context_data(self, **kwargs):
        context = super(QualifConceptTermUpdate, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['language_system'] = get_language()

        if IdentifierQualif.objects.count() > 0:
            context['next_id'] = int(IdentifierQualif.objects.latest('id').id)
        else:
            context['next_id'] = 1


        if self.request.method == 'GET':

            context['formset_concept'] = ConceptListQualifFormSet(instance=self.object)
            context['formset_term'] = TermListQualifFormSet(instance=self.object)

        return context



class QualifCreateView2(QualifConceptTermUpdate, CreateView):
    """
    Used as class view to create qualifier
    """
    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(QualifCreateView2, self).dispatch(*args, **kwargs)


    def get_success_url(self):

        id_concept = self.object.id

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( id_term, ths )




# Pesquisa ID do registro para poder saber qual é o ID do conceito destino
class ConceptListQualifView(LoginRequiredView, ListView):
    """
    List descriptor records (used by relationship popup selection window)
    """
    template_name = "thesaurus/search_concept_qualif.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['choiced_concept_identifier_id']:
            concept_identifier_id = self.actions['choiced_concept_identifier_id']

        if self.actions['s']:
            try:
                id_registro = IdentifierQualif.objects.filter(qualifier_ui=self.actions['s'],thesaurus=self.request.GET.get("ths")).values('id')
                if len(id_registro)>0:
                    id_registro = id_registro[0].get('id')
                    # Força somente 1 resultado
                    object_list = IdentifierConceptListQualif.objects.filter(identifier_id=id_registro).values('identifier_id','termqualif__term_string','termqualif__language_code','termqualif__id')[:1]
            except IdentifierQualif.DoesNotExist:
                # order performance -------------------------------------------------------------------------------------
                if self.actions['order'] == "-":
                    object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

                if self.actions['visited'] != 'ok':
                    object_list = object_list.none()


        return object_list

    def get_context_data(self, **kwargs):
        context = super(ConceptListQualifView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['actions'] = self.actions

        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['s']:
            try:
                # Força somente 1 resultado
                id_registro = IdentifierQualif.objects.filter(qualifier_ui=self.actions['s']).values('id')[:1]
                if len(id_registro)>0:
                    id_registro = id_registro[0].get('id')

                    # IdentifierQualif
                    context['id_register_objects'] = IdentifierQualif.objects.filter(
                                                    id=id_registro,
                                                    ).values(
                                                        # IdentifierQualif
                                                        'id',
                                                        'thesaurus',
                                                        'qualifier_ui',
                                                        'decs_code',
                                                        'external_code',
                                                        'date_created',
                                                        'date_revised',
                                                        'date_established',
                                                        'abbreviation',
                                                    )
                    context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

            except IdentifierQualif.DoesNotExist:
                context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

        return context



def ConceptListQualifModification(request,term_id, ths, concept_ori):

    # Descobre qual é o id do conceito do termo destino
    id_concept_destino = TermListQualif.objects.filter(id=term_id).values('identifier_concept_id')
    id_concept_destino = id_concept_destino[0].get('identifier_concept_id')

    identifier_id_destino = IdentifierConceptListQualif.objects.filter(id=id_concept_destino).values('identifier_id')
    identifier_id_destino = identifier_id_destino[0].get('identifier_id')

    # Verifica se o conceito é preferido, se for deverá ser escolhido o proximo nao preferido que assumirá a predileção
    check_preferred_concept_origem = IdentifierConceptListQualif.objects.filter(id=concept_ori).values('preferred_concept')
    check_preferred_concept_origem = check_preferred_concept_origem[0].get('preferred_concept')

    # Como o registro em TermListDesc será nao preferido, record_preferred_term deverá ser N obrigatoriamente no destino
    # Para isso, devo trazer todos os registros de concept_ori e atualizá-los
    TermListQualif.objects.filter(identifier_concept_id=concept_ori).update(record_preferred_term='N')

    if check_preferred_concept_origem == 'Y':

        # Verifica se o conceito origem tem irmãos, se houver e se o conceito origem for preferido então o segundo conceito assumirá a predileção
        check_concept_id_origem = IdentifierConceptListQualif.objects.filter(id=concept_ori).values('identifier_id')
        check_concept_id_origem = check_concept_id_origem[0].get('identifier_id')

        check_concept_id_origem = IdentifierConceptListQualif.objects.filter(identifier_id=check_concept_id_origem).values('identifier_id')

        if len(check_concept_id_origem) > 1:

            # Descobre qual o id do primeiro registro nao preferido
            check_concept_id_not_preferred = IdentifierConceptListQualif.objects.filter(identifier_id=check_concept_id_origem,preferred_concept='N').values('id')
            check_concept_id_not_preferred = check_concept_id_not_preferred[0].get('id')

            # Atualiza o identifier_id do conceito antigo para novo numero identifier_id_destino
            IdentifierConceptListQualif.objects.filter(id=check_concept_id_not_preferred).update(concept_relation_name='',preferred_concept='Y')

            # Necessário atualizar também os termos que são preferidos no conceito para também preferidos do registro
            TermListQualif.objects.filter(identifier_concept_id=check_concept_id_not_preferred, concept_preferred_term='Y').update(record_preferred_term='Y')

    # Atualiza o identifier_id do conceito antigo para novo numero identifier_id_destino
    # Atualiza o campo de histórico gravando informação de que registro foi originado
    identifier_id_ori = IdentifierConceptListQualif.objects.filter(id=concept_ori).values('identifier_id')
    identifier_id_ori = identifier_id_ori[0].get('identifier_id')
    qualifier_ui_ori = IdentifierQualif.objects.filter(id=identifier_id_ori).values('qualifier_ui')
    qualifier_ui_ori = qualifier_ui_ori[0].get('qualifier_ui')

    # Verifica se já existe anotação no historico
    has_hist=IdentifierConceptListQualif.objects.filter(id=concept_ori).exclude(historical_annotation__isnull=True).exclude(historical_annotation='').values('id','historical_annotation')
    if len(has_hist)>0:
        historical_annotation_old=has_hist[0].get('historical_annotation')
        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + str(qualifier_ui_ori)
        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')
    else:
        historical_annotation_new=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + str(qualifier_ui_ori)

    IdentifierConceptListQualif.objects.filter(id=concept_ori).update(identifier_id=identifier_id_destino,concept_relation_name='NRW',preferred_concept='N', historical_annotation=historical_annotation_new)


    url = '/thesaurus/qualifiers/view/' + term_id + '?ths=' + ths
    return HttpResponseRedirect(url)




# Pesquisa conceito para poder trazer ID do registro para novo conceito
# Não está sendo utilizado por enquanto
class TermListQualifView(LoginRequiredView, ListView):
    """
    List descriptor records (used by relationship popup selection window)
    """
    template_name = "thesaurus/search_term_qualif.html"
    context_object_name = "registers"
    paginate_by = ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['choiced_concept_identifier_id']:
            concept_identifier_id = self.actions['choiced_concept_identifier_id']

        if self.actions['s']:
            try:
                # Como o concept_ui pode existir em mais de um tesauro devemos descobrir qual o id em IdentifierQualif que é pertinente ao tesauro em questão
                concepts = IdentifierConceptListQualif.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
                for x in concepts:
                    id_identifier = x.get('identifier_id')
                    has_register = IdentifierQualif.objects.filter(id=id_identifier,thesaurus_id=self.request.GET.get("ths")).exists()
                    if has_register:
                        # Força somente 1 resultado
                        object_list = IdentifierConceptListQualif.objects.filter(concept_ui=self.actions['s'],identifier_id=id_identifier).values('identifier_id','termqualif__term_string','termqualif__language_code','termqualif__id')[:1]

            except IdentifierConceptListQualif.DoesNotExist:
                # order performance -------------------------------------------------------------------------------------
                if self.actions['order'] == "-":
                    object_list = object_list.order_by("%s%s" % (self.actions["order"], self.actions["orderby"]))

                if self.actions['visited'] != 'ok':
                    object_list = object_list.none()

        return object_list

    def get_context_data(self, **kwargs):
        context = super(TermListQualifView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        context['actions'] = self.actions

        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['s']:
            try:
                concepts = IdentifierConceptListQualif.objects.filter(concept_ui=self.actions['s']).values('identifier_id')
                for x in concepts:
                    id_identifier = x.get('identifier_id')
                    # print 'IDs --->',id_identifier
                    has_register = IdentifierQualif.objects.filter(id=id_identifier,thesaurus_id=self.request.GET.get("ths")).exists()
                    if has_register:
                        # print 'ID pertinente',id_identifier

                        # IdentifierQualif
                        context['id_register_objects'] = IdentifierConceptListQualif.objects.filter(
                                                        concept_ui=self.actions['s'],identifier_id=id_identifier
                                                        ).values(
                                                            # IdentifierConceptListDesc
                                                            'id',
                                                            'concept_ui',
                                                        )
                        context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']
            except IdentifierQualif.DoesNotExist:
                context['identifier_concept_id'] = self.actions['choiced_concept_identifier_id']

        return context



def TermListQualifModification(request,term_id, ths, term_ori):

    # Descobre qual é o identifier_concept_id do termo destino
    id_concept_destino = TermListQualif.objects.filter(id=term_id).values('identifier_concept_id')

    # Descobre qual é o identifier_id do conceito
    identifier_id_destino = IdentifierConceptListQualif.objects.filter(id=id_concept_destino).values('identifier_id')
    identifier_id_destino = identifier_id_destino[0].get('identifier_id')
    id_concept_destino = id_concept_destino[0].get('identifier_concept_id')

    # Descobre qual é o identifier_concept_id do termo origem
    term_origem_values = TermListQualif.objects.filter(id=term_ori).values('identifier_concept_id','term_ui')
    id_concept_origem = term_origem_values[0].get('identifier_concept_id')
    term_ui_origem = term_origem_values[0].get('term_ui')

    qtd_id_concept_origem = TermListQualif.objects.filter(identifier_concept_id=id_concept_origem)
    if len(qtd_id_concept_origem) == 1:
        # Quando existe apenas um termo para o conceito, deverá ser atualizado para a informação do novo conceito:
        # TermListQualif --> campo identifier_concept_id --> recebe valor do identifier_concept_id do termo destino
        # IdentifierConceptListQualif --> campo identifier_id --> recebe o valor do identifier_id do conceito destino

        # Atualiza o identifier_id do conceito antigo para novo numero identifier_id_destino
        IdentifierConceptListQualif.objects.filter(id=id_concept_origem).update(identifier_id=identifier_id_destino,concept_relation_name='NRW',preferred_concept='N')

    # Atualiza informações do termo origem e destino
    # Prepara informacoes do historico origem
    concept_ui_origem = IdentifierConceptListQualif.objects.filter(id=id_concept_origem).values('concept_ui')
    concept_ui_origem = concept_ui_origem[0].get('concept_ui')
    historical_annotation_old=TermListQualif.objects.filter(id=term_ori).values('id','historical_annotation')
    historical_annotation_old=historical_annotation_old[0].get('historical_annotation')

    # Armazena informacao para histórico destino
    historical_annotation_old_origem=historical_annotation_old

    # Prepara informacoes do historico destino
    concept_ui_destino = IdentifierConceptListQualif.objects.filter(id=id_concept_destino).values('concept_ui')
    concept_ui_destino = concept_ui_destino[0].get('concept_ui')
    historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', sent to ' + concept_ui_destino
    historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')

    # Atualiza historico da origem
    TermListQualif.objects.filter(id=term_ori).update(status=-3,historical_annotation=historical_annotation_new, date_altered=datetime.datetime.now().strftime('%Y-%m-%d'))

    # Pesquisa a existencia de um registro existente no destino com o status de migracao - 3
    # para isso pesquisa o term_ui de origem e o status=-3
    new_term=TermListQualif.objects.filter(id=term_ori).values('status','term_ui','language_code','term_string','concept_preferred_term','is_permuted_term','lexical_tag','record_preferred_term','entry_version','date_created','date_altered','historical_annotation','term_thesaurus','identifier_concept_id',)
    term_ui_ori=new_term[0].get('term_ui')
    term_string_ori=new_term[0].get('term_string').encode('utf-8')

    exist_term=TermListQualif.objects.filter(status=-3, term_ui=term_ui_ori, term_string=term_string_ori, identifier_concept_id=id_concept_destino).values('id','historical_annotation')

    if len(exist_term) > 0:
        term_id_exist=exist_term[0].get('id')
        historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + concept_ui_origem
        historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')

        # Atualiza o historico do destino
        TermListQualif.objects.filter(id=term_id_exist).update(status='1',concept_preferred_term='N',is_permuted_term='N',record_preferred_term='N',historical_annotation=historical_annotation_new, date_altered=datetime.datetime.now().strftime('%Y-%m-%d'))

    else:
        # Cria nova entrada
        item = TermListQualif.objects.create(
                status='1',
                term_ui=new_term[0].get('term_ui'),
                language_code=new_term[0].get('language_code'),
                term_string=new_term[0].get('term_string'),
                concept_preferred_term='N',
                is_permuted_term='N',
                lexical_tag=new_term[0].get('lexical_tag'),
                record_preferred_term='N',
                entry_version=new_term[0].get('entry_version'),
                date_created=new_term[0].get('date_created'),
                date_altered=datetime.datetime.now().strftime('%Y-%m-%d'),
                historical_annotation=datetime.datetime.now().strftime('%Y-%m-%d') + ', received from ' + concept_ui_origem + ';' + historical_annotation_old_origem,
                term_thesaurus=new_term[0].get('term_thesaurus'),
                identifier_concept_id=id_concept_destino,
                )
    url = '/thesaurus/qualifiers/view/' + term_ori + '?ths=' + ths
    return HttpResponseRedirect(url)



class TermCreateQualifConfirm(LoginRequiredView, TemplateView):

    template_name = 'thesaurus/confirm_create_qualif.html'

    def get_context_data(self, **kwargs):
        context = super(TermCreateQualifConfirm, self).get_context_data(**kwargs)
        thesaurus_name = Thesaurus.objects.filter(id=self.request.GET.get("ths")).values('thesaurus_name')
        context['thesaurus_name'] = thesaurus_name[0].get('thesaurus_name')

        return context



def TermCreateQualifDo(request, ths):

    term_string = request.GET.get("term_string")
    language_code = request.GET.get("language_code")
    term_ui = request.GET.get("term_ui")
    term_id = request.GET.get("term_id")

    return redirect('/thesaurus/qualifiers/new/?ths=' + ths + '&term=' + term_string + '&language_code=' + language_code + '&term_ui=' + term_ui + '&term_id=' + term_id)




class ConceptCreateQualifConfirm(LoginRequiredView, ListView):
    """
    Used to verify if already exist the term
    """
    template_name = "thesaurus/confirm_create_register_qualif.html"
    context_object_name = "registers"


    def get_queryset(self):
        object_list = []

        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        return object_list


    def get_context_data(self, **kwargs):
        context = super(ConceptCreateQualifConfirm, self).get_context_data(**kwargs)

        context['choiced_thesaurus'] = self.request.GET.get("choiced_thesaurus")
        context['choiced_abbreviation'] = self.request.GET.get("abbreviation")

        return context


    def render_to_response(self, context):
        # getting action parameter
        self.actions = {}
        for key in ACTIONS.keys():
            self.actions[key] = self.request.GET.get(key, ACTIONS[key])

        if self.actions['term_string'] and self.actions['filter_language']:

            ths = self.actions['choiced_thesaurus']
            term_string = self.actions['term_string']
            language_code = self.actions['filter_language']
            concept_id = self.request.GET.get("concept_id")
            term_id = self.request.GET.get("term_id")
            created_by = self.request.GET.get("created_by")
            abbreviation = self.request.GET.get("abbreviation").upper()

            # print 'Abbreviation--->',abbreviation
            
            thesaurus_name = self.request.GET.get("choiced_thesaurus_name")

            # print 'DEBUG'
            # print '[ths - ' ,ths,' ]'
            # print '[term_string - ' ,term_string,' ]'
            # print '[language_code - ' ,language_code,' ]'
            # print '[concept_id - ' ,concept_id,' ]'
            # print '[term_id - ' ,term_id,' ]'
            # print '[created_by - ' ,created_by,' ]'
            # print '[abbreviation - ' ,abbreviation,' ]'
            # print '[thesaurus_name - ' ,thesaurus_name,' ]'
            # print 'DEBUG'

            # Verifica a existencia da combinação de abbreviation e thesaurus, se existir não deverá ser permitido
            has_abbreviation = IdentifierQualif.objects.filter(abbreviation=abbreviation,thesaurus=ths).exists()
            if not has_abbreviation:

                # Descobrindo qual é o descriptor_ui do registro origem
                identifier_id_ori = IdentifierConceptListQualif.objects.filter(id=concept_id).values('identifier_id')
                identifier_id_ori = identifier_id_ori[0].get('identifier_id')
                qualifier_ui_ori = IdentifierQualif.objects.filter(id=identifier_id_ori).values('qualifier_ui')
                qualifier_ui_ori = qualifier_ui_ori[0].get('qualifier_ui')

                # Verifica se já existe anotação no historico
                has_hist=IdentifierConceptListQualif.objects.filter(id=concept_id).values('historical_annotation')
                if has_hist:
                    historical_annotation_old=has_hist[0].get('historical_annotation')
                    historical_annotation_now=datetime.datetime.now().strftime('%Y-%m-%d') + ', turned into record - received from ' + str(qualifier_ui_ori)
                    historical_annotation_new=historical_annotation_now.encode('utf-8') + ';' + historical_annotation_old.encode('utf-8')

                created_time=datetime.datetime.now().strftime('%Y-%m-%d')
                created_time = created_time.encode('utf-8')

                # Get sequential number to write to decs_code
                try:
                    seq = code_controller.objects.get(thesaurus=ths)
                    nseq = str(int(seq.sequential_number) + 1)
                    seq.sequential_number = nseq
                    seq.save()
                except code_controller.DoesNotExist:
                    seq = code_controller(sequential_number=1,thesaurus=ths)
                    nseq = 1
                    seq.save()
                decs_code=nseq

                # Get thesaurus_acronym to create new ID format to descriptor_ui field
                try:
                    acronym = Thesaurus.objects.filter(id=ths).values('thesaurus_acronym')
                    # recupera o acronimo e transforma em maiusuclo
                    acronym = str(acronym[0].get('thesaurus_acronym')).upper()
                    # utiliza self.object.decs_code para compor descriptor_ui
                    zseq = str(nseq).zfill(6) # preenche zeros a esquerda
                    qualifier_ui = 'Q' + acronym + zseq
                except Thesaurus.DoesNotExist:
                    id_thesaurus = str(self.object.id)
                    print 'Warning! - No thesaurus_acronym for id -->',id_thesaurus

                add_reg = IdentifierQualif(qualifier_ui=qualifier_ui, decs_code=decs_code, abbreviation=abbreviation, date_created=created_time, created_by_id=created_by, thesaurus_id=ths)
                add_reg.save()

                # # Descobrindo último ID inserido
                last_id = IdentifierQualif.objects.filter(thesaurus_id=ths).order_by('id').last()

                # Atualiza identifier_id antigo para novo id, apaga concept_relation_name, atualiza preferred_concept como preferido e atualiza hsitórico
                update_field = IdentifierConceptListQualif.objects.get(id=concept_id)
                update_field.identifier_id = last_id
                update_field.concept_relation_name = ""
                update_field.preferred_concept = "Y"
                update_field.historical_annotation = historical_annotation_new
                update_field.save()

                # Atualiza record_preferred_term dos Termos que foram elegidos como preferidos no registro novo
                update_registers = TermListQualif.objects.filter(identifier_concept_id=concept_id, concept_preferred_term='Y', record_preferred_term='N')
                if update_registers:
                    for upd in update_registers:
                        TermListQualif.objects.filter(id=str(upd)).update(record_preferred_term='Y')

                return redirect('/thesaurus/qualifiers/view/' + term_id + '?ths=' + ths)
            else:
                return redirect('/thesaurus/qualifiers/create/concept/confirm/?ths=' + ths + '&term_string=' + term_string + '&language_code=' + language_code + '&concept_id=' + concept_id + '&term_id=' + term_id + '&created_by=' + created_by + '&thesaurus_name=' +  thesaurus_name + '&has_abbreviation=' + abbreviation )

        return super(ConceptCreateQualifConfirm, self).render_to_response(context)




class ConceptListQualifCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create concept and term of qualifier
    """
    model = IdentifierConceptListQualif
    template_name = 'thesaurus/qualifier_new_concept.html'
    form_class = IdentifierConceptListQualifForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(ConceptListQualifCreateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):

        id_concept = self.object.id

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( id_term, ths )


    def form_valid(self, form):

        formset_concept = ConceptListQualifFormSet(self.request.POST, instance=self.object)
        formset_term = TermListQualifFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_concept_valid and formset_term_valid):
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("termqualif-0-term_string")
            language_code = self.request.POST.get("termqualif-0-language_code")
            term_thesaurus = self.request.GET.get("ths")

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=5,
                                )

            has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_string.encode('utf-8'):
                    # print 'Igual-->',t
                    has_equal=t

            if not has_equal:
                self.object = form.save(commit=False)
                self.object.identifier_id = int(self.request.POST.get("identifier_id"))
                self.object = form.save(commit=True)

                formset_concept.instance = self.object
                formset_concept.save()

                formset_term.instance = self.object
                formset_term.save()

                # Bring the choiced language_code from the first form
                registry_language = formset_term.cleaned_data[0].get('language_code')

                form.save()

                # Update concept_ui with a new format
                try:
                    created_concept_id = int(IdentifierConceptListQualif.objects.latest('id').id)
                    update_concept_field = IdentifierConceptListQualif.objects.get(id=created_concept_id)

                    # preenche zeros a esquerda
                    zseq = str(created_concept_id).zfill(8)

                    update_concept_field.concept_ui = 'FQ' + zseq
                    update_concept_field.save()
                except IdentifierConceptListQualif.DoesNotExist:
                    print 'Warning! Does not exist id to this Concept'

                # Update term_ui with a new format
                try:

                    ths = self.request.GET.get("ths")
                    try:
                        seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                        nseq = str(int(seq.sequential_number) + 1)
                        seq.sequential_number = nseq
                        seq.save()
                    except code_controller_term.DoesNotExist:
                        seq = code_controller_term(sequential_number=1,thesaurus=ths)
                        nseq = 1
                        seq.save()
                    created_id = int(TermListQualif.objects.latest('id').id)
                    update_field = TermListQualif.objects.get(id=created_id)

                    # substitui idioma do sistema por sigla de 3 letras
                    if registry_language == 'en':
                        language_3letters = 'eng'
                    if registry_language == 'es':
                        language_3letters = 'spa'
                    if registry_language == 'pt-br':
                        language_3letters = 'por'
                    if registry_language == 'fr':
                        language_3letters = 'fre'
                    if registry_language == 'es-es':
                        language_3letters = 'spa'

                    # preenche zeros a esquerda
                    zseq = str(nseq).zfill(6)

                    update_field.term_ui = language_3letters + 'q' + zseq
                    update_field.save()
                except TermListQualif.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                # Update created_date
                try:
                    created_id = int(TermListQualif.objects.latest('id').id)
                    update_date_created = TermListQualif.objects.get(id=created_id)
                    update_date_created.date_created = datetime.datetime.now().strftime('%Y-%m-%d')
                    update_date_created.save()
                except TermListQualif.DoesNotExist:
                    print 'Warning! Does not exist id to this Term'

                return HttpResponseRedirect(self.get_success_url())
            else:
                msg_erro =  _("This Concept already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                form=form,
                                                formset_concept=formset_concept,
                                                formset_term=formset_term,
                                                msg_erro=msg_erro,
                                                ))

    def get_context_data(self, **kwargs):
        context = super(ConceptListQualifCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.method == 'GET':

            context['formset_concept'] = ConceptListQualifFormSet(instance=self.object)
            context['formset_term'] = TermListQualifFormSet(instance=self.object)

        return context



class ConceptListQualifUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update a concept of qualifier
    """
    model = IdentifierConceptListQualif
    template_name = 'thesaurus/qualifier_edit_concept.html'
    form_class = IdentifierConceptListQualifForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(ConceptListQualifUpdateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( int(self.request.POST.get("termqualif__id")), ths )


    def form_valid(self, form):

        formset_concept = ConceptListQualifFormSet(self.request.POST, instance=self.object)

        form_valid = form.is_valid()
        formset_concept_valid = formset_concept.is_valid()

        if (form_valid and formset_concept_valid):

            self.object = form.save(commit=False)
            self.object.identifier_id = int(self.request.POST.get("identifier_id"))

            formset_concept.instance = self.object
            formset_concept.save()

            form.save()

            # Necessário atualizar também os termos que são preferidos no conceito para também preferidos do registro
            # print 'id ----->',self.object.id
            check_preferred_concept = self.request.POST.get("preferred_concept")
            # print 'check_preferred_concept ---->',check_preferred_concept

            if check_preferred_concept == 'Y':
                TermListQualif.objects.filter(identifier_concept_id=self.object.id, concept_preferred_term='Y').update(record_preferred_term='Y')
            else:
                TermListQualif.objects.filter(identifier_concept_id=self.object.id, concept_preferred_term='Y').update(record_preferred_term='N')

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(
                                            form=form,
                                            formset_concept=formset_concept,
                                            )
                        )

    def get_context_data(self, **kwargs):
        context = super(ConceptListQualifUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        if self.request.method == 'GET':
            context['formset_concept'] = ConceptListQualifFormSet(instance=self.object)
        return context




class TermListQualifCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create a term
    """
    model = TermListQualif
    template_name = 'thesaurus/qualifier_new_term.html'
    form_class = TermListQualifUniqueForm

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(TermListQualifCreateView, self).dispatch(*args, **kwargs)


    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( self.object.id, ths )

    def form_valid(self, form):
        
        if form.is_valid():
            # Brings form variables to check if it already exists
            term_string = self.request.POST.get("term_string")
            language_code = self.request.POST.get("language_code")
            concept_preferred_term = self.request.POST.get("concept_preferred_term")
            record_preferred_term = self.request.POST.get("record_preferred_term")
            identifier_concept_id = self.request.POST.get("identifier_concept_id")
            term_thesaurus = self.request.GET.get("ths")

            if concept_preferred_term == 'Y' and record_preferred_term == 'Y':
                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by published record
                q_status_published = Q(
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    concept_preferred_term="Y",
                                    record_preferred_term="Y",
                                    identifier_concept_id=identifier_concept_id,
                                    # status=1,
                                    )

            if concept_preferred_term == 'Y' and record_preferred_term == 'N':
                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by published record
                q_status_published = Q(
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    concept_preferred_term="Y",
                                    record_preferred_term="N",
                                    identifier_concept_id=identifier_concept_id,
                                    # status=1,
                                    )

            if ( concept_preferred_term == 'Y' and record_preferred_term == 'Y' ) or ( concept_preferred_term == 'Y' and record_preferred_term == 'N' ):

                has_term_config = TermListQualif.objects.filter( q_status_published ).values('id')

                if len(has_term_config) > 0:

                    msg_erro =  _("This configuration already exists for this concept!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        msg_erro=msg_erro,
                                                                        ))
                else:

                    # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"

                    # Para poder criar um termo novo, não deve existir
                    # -1 - Rascunho
                    # 1  - Publicado
                    # 5  - Histórico

                    # Search by draft record
                    q_status_draft = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=-1,
                                        )

                    # Search by published record
                    q_status_published = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=1,
                                        )

                    # Search by historical record
                    q_status_historical = Q(
                                        term_string__exact=term_string,
                                        language_code=language_code,
                                        term_thesaurus=term_thesaurus,
                                        status=5,
                                        )

                    has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

                    # Corre resultados e compara
                    has_equal=''
                    for term in has_term:
                        t=term.get('term_string').encode('utf-8')
                        if t == term_string.encode('utf-8'):
                            # print 'Igual-->',t
                            has_equal=t

                    if not has_equal:
                        self.object = form.save(commit=False)

                        # prove the current date if you are not informed on the form
                        if not self.object.date_created:
                            self.object.date_created = datetime.datetime.now().strftime('%Y-%m-%d')

                        self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                        form.save()

                        registry_language = self.request.POST.get("language_code")

                        # Update term_ui with a new format
                        try:

                            ths = self.request.GET.get("ths")
                            try:
                                seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                                nseq = str(int(seq.sequential_number) + 1)
                                seq.sequential_number = nseq
                                seq.save()
                            except code_controller_term.DoesNotExist:
                                seq = code_controller_term(sequential_number=1,thesaurus=ths)
                                nseq = 1
                                seq.save()
                            created_id = int(TermListQualif.objects.latest('id').id)
                            update_field = TermListQualif.objects.get(id=created_id)

                            # substitui idioma do sistema por sigla de 3 letras
                            if registry_language == 'en':
                                language_3letters = 'eng'
                            if registry_language == 'es':
                                language_3letters = 'spa'
                            if registry_language == 'pt-br':
                                language_3letters = 'por'
                            if registry_language == 'fr':
                                language_3letters = 'fre'
                            if registry_language == 'es-es':
                                language_3letters = 'spa'

                            # preenche zeros a esquerda
                            zseq = str(nseq).zfill(6)

                            update_field.term_ui = language_3letters + 'q' + zseq
                            update_field.save()
                        except TermListQualif.DoesNotExist:
                            print 'Warning! Does not exist id to this Term'

                        return HttpResponseRedirect(self.get_success_url())
                    else:
                        msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                        return self.render_to_response(self.get_context_data(form=form,msg_erro=msg_erro))
            else:
                # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
                # Search by draft record
                q_status_draft = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=-1,
                                    )

                # Search by published record
                q_status_published = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=1,
                                    )

                # Search by historical record
                q_status_historical = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=5,
                                    )

                has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).values('term_string')

                # Corre resultados e compara
                has_equal=''
                for term in has_term:
                    t=term.get('term_string').encode('utf-8')
                    if t == term_string.encode('utf-8'):
                        # print 'Igual-->',t
                        has_equal=t

                if not has_equal:
                    self.object = form.save(commit=False)

                    # prove the current date if you are not informed on the form
                    if not self.object.date_created:
                        self.object.date_created = datetime.datetime.now().strftime('%Y-%m-%d')

                    self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                    form.save()

                    registry_language = self.request.POST.get("language_code")

                    # Update term_ui with a new format
                    try:

                        ths = self.request.GET.get("ths")
                        try:
                            seq = code_controller_term.objects.get(thesaurus=self.request.GET.get("ths"))
                            nseq = str(int(seq.sequential_number) + 1)
                            seq.sequential_number = nseq
                            seq.save()
                        except code_controller_term.DoesNotExist:
                            seq = code_controller_term(sequential_number=1,thesaurus=ths)
                            nseq = 1
                            seq.save()
                        created_id = int(TermListQualif.objects.latest('id').id)
                        update_field = TermListQualif.objects.get(id=created_id)

                        # substitui idioma do sistema por sigla de 3 letras
                        if registry_language == 'en':
                            language_3letters = 'eng'
                        if registry_language == 'es':
                            language_3letters = 'spa'
                        if registry_language == 'pt-br':
                            language_3letters = 'por'
                        if registry_language == 'fr':
                            language_3letters = 'fre'
                        if registry_language == 'es-es':
                            language_3letters = 'spa'

                        # preenche zeros a esquerda
                        zseq = str(nseq).zfill(6)

                        update_field.term_ui = language_3letters + 'q' + zseq
                        update_field.save()
                    except TermListQualif.DoesNotExist:
                        print 'Warning! Does not exist id to this Term'

                    return HttpResponseRedirect(self.get_success_url())
                else:
                    msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(form=form,msg_erro=msg_erro))

    def get_context_data(self, **kwargs):
        context = super(TermListQualifCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context



class TermListQualifUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update a term
    """
    model = TermListQualif
    template_name = 'thesaurus/qualifier_edit_term.html'
    form_class = TermListQualifUniqueForm

    def get_success_url(self):
        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s' % ( self.object.id, ths )

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(TermListQualifUpdateView, self).dispatch(*args, **kwargs)


    def form_valid(self, form):

        # Armazena string de term_string para popular historico
        term_string_current = TermListQualif.objects.filter(id=self.object.id).values('term_string','concept_preferred_term','record_preferred_term','historical_annotation')
        for y in term_string_current:
            term_string_old=y.get('term_string')
            concept_preferred_term_old=y.get('concept_preferred_term')
            record_preferred_term_old=y.get('record_preferred_term')
            historical_annotation_old=y.get('historical_annotation')
            # print 'Current - TERM ----->',term_string_old
            # print 'Current - Historico --->',historical_annotation_old

        # Brings form variables to check if it already exists
        term_string = self.request.POST.get("term_string")
        language_code = self.request.POST.get("language_code")
        concept_preferred_term = self.request.POST.get("concept_preferred_term")
        record_preferred_term = self.request.POST.get("record_preferred_term")
        identifier_concept_id = self.request.POST.get("identifier_concept_id")
        term_thesaurus = self.request.GET.get("ths")

        # Username
        user_data = additional_user_info(self.request)
        for user_name in user_data:
            username=user_data.get('user_name').encode('utf-8')
            break

        v998='^d' + datetime.datetime.now().strftime('%Y-%m-%d') + '^h' + term_string_old + '^u' + username + '^t'

        # Se ocorreu alteracao
        # Grava configuração anterior
        # concept_preferred_term_old
        # Decide prenchimento com [ 01, 02, 03, 04 ou 16 ] ou [ 51, 52, 53, 54 e 516]
        if concept_preferred_term_old == 'Y':
            if language_code == 'en':
                sub_t='01'
            if language_code == 'es':
                sub_t='02'
            if language_code == 'pt-br':
                sub_t='03'
            if language_code == 'es-es':
                sub_t='04'
            if language_code == 'fr':
                sub_t='16'
        else:
            if language_code == 'en':
                sub_t='51'
            if language_code == 'es':
                sub_t='52'
            if language_code == 'pt-br':
                sub_t='53'
            if language_code == 'es-es':
                sub_t='54'
            if language_code == 'fr':
                sub_t='516'
        term_string_historical = v998 + sub_t

        if concept_preferred_term == 'Y' and record_preferred_term == 'Y':

            # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
            # Search by published record
            q_status_published = Q(
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                concept_preferred_term="Y",
                                record_preferred_term="Y",
                                identifier_concept_id=identifier_concept_id,
                                # status=1,
                                )

        if concept_preferred_term == 'Y' and record_preferred_term == 'N':

            # Verifica se já não existe configuração para esse conceito com mesmo language_code, concept_preferred_term = "Y" e record_preferred_term = "Y"
            # Search by published record
            q_status_published = Q(
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                concept_preferred_term="Y",
                                record_preferred_term="N",
                                identifier_concept_id=identifier_concept_id,
                                # status=1,
                                )

        if ( concept_preferred_term == 'Y' and record_preferred_term == 'Y' ) or ( concept_preferred_term == 'Y' and record_preferred_term == 'N' ):

            has_term_config = TermListQualif.objects.filter( q_status_published ).values('id').exclude(id=self.object.id,)

            if len(has_term_config) > 0:

                msg_erro =  _("This configuration already exists for this concept!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                                    form=form,
                                                                    msg_erro=msg_erro,
                                                                    ))
            else:

                # Search by draft record
                q_status_draft = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=-1,
                                    )

                # Search by published record
                q_status_published = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=1,
                                    )

                # Search by historical record
                q_status_historical = Q(
                                    term_string__exact=term_string,
                                    language_code=language_code,
                                    term_thesaurus=term_thesaurus,
                                    status=5,
                                    )

                has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).exclude(id=self.object.id).values('term_string')

                # Corre resultados e compara
                has_equal=''
                for term in has_term:
                    t=term.get('term_string').encode('utf-8')
                    if t == term_string.encode('utf-8'):
                        # print 'Igual-->',t
                        has_equal=t

                if has_equal:
                    msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        msg_erro=msg_erro,
                                                                        ))
                else:

                    form_valid = form.is_valid()

                    if form_valid:

                        self.object = form.save(commit=False)

                        self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                        self.object.date_altered = datetime.datetime.now().strftime('%Y-%m-%d')

                        term_string_historical = v998 + sub_t

                        if len(historical_annotation_old) > 0:
                            term_string_historical=term_string_historical + ';' + historical_annotation_old

                        self.object.historical_annotation = term_string_historical

                        self.object = form.save(commit=True)

                        form.save()
                        return HttpResponseRedirect(self.get_success_url())

                    else:
                        return self.render_to_response(self.get_context_data(
                                                                            form=form,
                                                                            ))
        else:

            # Search by draft record
            q_status_draft = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=-1,
                                )

            # Search by published record
            q_status_published = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=1,
                                )

            # Search by historical record
            q_status_historical = Q(
                                term_string__exact=term_string,
                                language_code=language_code,
                                term_thesaurus=term_thesaurus,
                                status=5,
                                )

            has_term = TermListQualif.objects.filter( q_status_draft | q_status_published | q_status_historical ).exclude(id=self.object.id).values('term_string')

            # Corre resultados e compara
            has_equal=''
            for term in has_term:
                t=term.get('term_string').encode('utf-8')
                if t == term_string.encode('utf-8'):
                    # print 'Igual-->',t
                    has_equal=t

            if has_equal:
                msg_erro =  _("This Term already exist!") + ' -----> ' + term_string + ' (' + language_code +  ')'
                return self.render_to_response(self.get_context_data(
                                                                    form=form,
                                                                    msg_erro=msg_erro,
                                                                    ))
            else:
                form_valid = form.is_valid()
                if form_valid:

                    self.object = form.save(commit=False)

                    self.object.identifier_concept_id = self.request.POST.get("identifier_concept_id")

                    self.object.date_altered = datetime.datetime.now().strftime('%Y-%m-%d')

                    term_string_historical = v998 + sub_t

                    if len(historical_annotation_old) > 0:
                        term_string_historical=term_string_historical + ';' + historical_annotation_old

                    self.object.historical_annotation = term_string_historical

                    self.object = form.save(commit=True)

                    form.save()
                    return HttpResponseRedirect(self.get_success_url())

                else:
                    return self.render_to_response(self.get_context_data(
                                                                        form=form,
                                                                        ))


    def get_context_data(self, **kwargs):
        context = super(TermListQualifUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context



class legacyInformationQualifCreateView(LoginRequiredView, CreateView):
    """
    Used as class view to create legacy information
    """
    model = legacyInformationQualif
    template_name = 'thesaurus/qualifier_new_legacy.html'
    form_class = legacyInformationQualifForm

    def get_success_url(self):

        id_identifier = self.request.GET.get("identifier_id")

        # Search ID of the first concept of this record
        concepts_of_registry = IdentifierConceptListQualif.objects.filter(identifier_id=id_identifier).values('id')
        id_concept = concepts_of_registry[0].get('id')

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s%s' % ( id_term, ths )

    def form_valid(self, form):

        if form.is_valid():

            self.object = form.save(commit=False)
            self.object.identifier_id = self.request.POST.get("identifier_id")
            self.object = form.save()
            form.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(legacyInformationQualifCreateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

        return context



class legacyInformationQualifUpdateView(LoginRequiredView, UpdateView):
    """
    Used as class view to update a legacy information
    """
    model = legacyInformationQualif
    template_name = 'thesaurus/qualifier_edit_legacy.html'
    form_class = legacyInformationQualifForm


    def get_success_url(self):

        id_identifier = self.request.GET.get("identifier_id")

        # Search ID of the first concept of this record
        concepts_of_registry = IdentifierConceptListQualif.objects.filter(identifier_id=id_identifier).values('id')
        id_concept = concepts_of_registry[0].get('id')

        # Search ID of the first term of this concept to redirect
        terms_of_concept = TermListQualif.objects.filter(identifier_concept_id=id_concept).values('id')
        id_term = terms_of_concept[0].get('id')

        ths = '?ths=' + self.request.GET.get("ths")
        return '/thesaurus/qualifiers/view/%s%s%s' % ( id_term, ths )

    def form_valid(self, form):

        if form.is_valid():

            self.object = form.save()
            form.save()

            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(legacyInformationQualifUpdateView, self).get_context_data(**kwargs)

        context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))
        
        return context



class PageViewQualif(LoginRequiredView, DetailView):
    """
    Used as class view to list the result
    """
    model = TermListQualif
    template_name = 'thesaurus/page_view_qualif.html'

    def dispatch(self, *args, **kwargs):
        user_data = additional_user_info(self.request)
        user_cc = user_data['user_cc']
        user_role = user_data['service_role']

        if user_cc != 'BR1.1':
            # Brings "ths" from the environment
            if self.request.GET.get("thesaurus"):
                environment_thesaurus_id=self.request.GET.get("thesaurus")
            else:
                if self.request.GET.get("ths"):
                    environment_thesaurus_id=self.request.GET.get("ths")

            access_status=False

            # Create array with all registered thesaurus
            ids_thesaurus = []
            ids_thesaurus = Thesaurus.objects.all().values('id','thesaurus_scope')

            # Run user_role array and compare the service registered to the user with the service registered in thesaurus.
            # If the service exists bring the id of that service and compare with the id that is in the environment at the moment, if not exist generates the deny page
            for role in user_role:
                user_service=role
                for elem in ids_thesaurus:
                    id_thesaurus = elem.get('id')
                    thesaurus_scope = elem.get('thesaurus_scope')
                    if user_service == thesaurus_scope and int(id_thesaurus) == int(environment_thesaurus_id):
                        access_status=True

            if access_status==False:
                return HttpResponseForbidden()

        return super(PageViewQualif, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(PageViewQualif, self).get_context_data(**kwargs)

        if self.object:

            # IdentifierConceptListQualif - recupera pk do conceito
            id_concept = IdentifierConceptListQualif.objects.filter(
                                            id=self.object.identifier_concept_id,
                                            ).values('identifier_id').distinct()

            # Used to create new concept
            for concept in id_concept:
                context['id_concept_new'] = concept

            # IdentifierConceptListQualif - retrieves pk's that has even identifier_id - can bring more than 1
            ids = IdentifierConceptListQualif.objects.filter(
                                            identifier_id=id_concept,
                                            ).values('id')

            # IdentifierQualif
            # Brings information to Active Descriptor Record
            context['identifierqualif_objects'] = IdentifierQualif.objects.filter(
                                            id=id_concept,
                                            )

            context['id_register_objects'] = IdentifierQualif.objects.filter(
                                            id=id_concept,
                                            ).values(

                                                # IdentifierQualif
                                                'id',
                                                'thesaurus',
                                                'qualifier_ui',
                                                'decs_code',
                                                'external_code',
                                                'abbreviation',
                                                'date_created',
                                                'date_revised',
                                                'date_established',
                                            )

            context['description_objects'] = IdentifierQualif.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # DescriptionQualif
                                                'descriptionqualif__identifier_id',
                                                'descriptionqualif__language_code',
                                                'descriptionqualif__annotation',
                                                'descriptionqualif__history_note',
                                                'descriptionqualif__online_note',
                                            )

            # Used to create tree number list
            context['tree_numbers_objects'] = IdentifierQualif.objects.filter(
                                            id=id_concept,
                                            ).values(
                                                # TreeNumbersListQualif
                                                'qtreenumbers__identifier_id',
                                                'qtreenumbers__tree_number',
                                            ).distinct().order_by('qtreenumbers__tree_number')

            context['term_string_info_preferred_objects'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,termqualif__concept_preferred_term='Y',termqualif__record_preferred_term='Y',
                                            ).order_by('identifier_id',
                                                        'termqualif__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termqualif__concept_preferred_term',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'id',
                                                    'termqualif__status',
                                                    'termqualif__term_string',
                                                    'termqualif__language_code',
                                                    'identifier_id',
                                            )

            context['entry_terms_objects'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,termqualif__status=1,termqualif__record_preferred_term='N',
                                            ).order_by('identifier_id',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'id',
                                                    'termqualif__id',
                                                    'termqualif__term_string',
                                                    'termqualif__language_code',
                                            )

            context['scope_note_objects'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by('identifier_id',
                                            ).values(
                                                    'conceptqualif__language_code',
                                                    'conceptqualif__scope_note',
                                            ).distinct()

            context['legacy_objects'] = legacyInformationQualif.objects.filter(
                                            identifier=id_concept,
                                            ).values(
                                                'id',
                                                'pre_codificado',
                                                'desastre',
                                                'reforma_saude',
                                                'geografico',
                                                'mesh',
                                                'pt_lilacs',
                                                'nao_indexavel',
                                                'homeopatia',
                                                'repidisca',
                                                'saude_publica',
                                                'exploded',
                                                'geog_decs',
                                                'identifier_id',
                                            )

            # Usado para mostrar informações de conceitos e termos Preferidos
            context['identifierconceptlist_objects_preferred'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by(
                                                        '-preferred_concept',
                                                        '-termqualif__concept_preferred_term',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'id',
                                                    'identifier_id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',
                                                    'casn1_name',
                                                    'registry_number',

                                                    'conceptqualif__identifier_concept_id',
                                                    'conceptqualif__language_code',
                                                    'conceptqualif__scope_note',

                                                    'termqualif__id',
                                                    'termqualif__identifier_concept_id',
                                                    'termqualif__status',
                                                    'termqualif__term_ui',
                                                    'termqualif__language_code',
                                                    'termqualif__term_string',
                                                    'termqualif__concept_preferred_term',
                                                    'termqualif__is_permuted_term',
                                                    'termqualif__lexical_tag',
                                                    'termqualif__record_preferred_term',
                                                    'termqualif__entry_version',
                                                    'termqualif__date_created',
                                                    'termqualif__date_altered',
                                                    'termqualif__historical_annotation',
                                            ).distinct()

            # Usado para mostrar informações de conceitos e termos Preferidos para Aba de Conceitos
            context['identifierconceptlist_objects_preferred_for_concepts'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,preferred_concept='Y',
                                            ).order_by(
                                                        '-preferred_concept',
                                                        '-termqualif__concept_preferred_term',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'identifier_id',
                                                    'id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',

                                                    'termqualif__id',
                                                    'termqualif__identifier_concept_id',
                                                    'termqualif__status',
                                                    'termqualif__term_ui',
                                                    'termqualif__language_code',
                                                    'termqualif__term_string',
                                                    'termqualif__concept_preferred_term',
                                                    'termqualif__is_permuted_term',
                                                    'termqualif__lexical_tag',
                                                    'termqualif__record_preferred_term',
                                                    'termqualif__entry_version',
                                                    'termqualif__date_created',
                                                    'termqualif__date_altered',
                                                    'termqualif__historical_annotation',
                                            ).distinct()

            # Usado para mostrar informações de conceitos e termos Não Preferidos
            context['identifierconceptlist_objects'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,preferred_concept='N',
                                            ).order_by('identifier_id',
                                                        'termqualif__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termqualif__concept_preferred_term',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'id',
                                                    'identifier_id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',
                                                    'casn1_name',
                                                    'registry_number',

                                                    'conceptqualif__identifier_concept_id',
                                                    'conceptqualif__language_code',
                                                    'conceptqualif__scope_note',

                                                    'termqualif__id',
                                                    'termqualif__identifier_concept_id',
                                                    'termqualif__status',
                                                    'termqualif__term_ui',
                                                    'termqualif__language_code',
                                                    'termqualif__term_string',
                                                    'termqualif__concept_preferred_term',
                                                    'termqualif__is_permuted_term',
                                                    'termqualif__lexical_tag',
                                                    'termqualif__record_preferred_term',
                                                    'termqualif__entry_version',
                                                    'termqualif__date_created',
                                                    'termqualif__date_altered',
                                                    'termqualif__historical_annotation',
                                            ).distinct()

            # Usado para mostrar informações de conceitos e termos Não Preferidos para Aba Conceitos
            context['identifierconceptlist_objects_for_concepts'] = IdentifierConceptListQualif.objects.filter(
                                            identifier=id_concept,preferred_concept='N',
                                            ).order_by('identifier_id',
                                                        'termqualif__identifier_concept_id',
                                                        '-preferred_concept',
                                                        '-termqualif__concept_preferred_term',
                                                        'termqualif__language_code',
                                                        'termqualif__term_string',
                                            ).values(
                                                    'identifier_id',
                                                    'id',
                                                    'concept_ui',
                                                    'concept_relation_name',
                                                    'preferred_concept',

                                                    'termqualif__id',
                                                    'termqualif__identifier_concept_id',
                                                    'termqualif__status',
                                                    'termqualif__term_ui',
                                                    'termqualif__language_code',
                                                    'termqualif__term_string',
                                                    'termqualif__concept_preferred_term',
                                                    'termqualif__is_permuted_term',
                                                    'termqualif__lexical_tag',
                                                    'termqualif__record_preferred_term',
                                                    'termqualif__entry_version',
                                                    'termqualif__date_created',
                                                    'termqualif__date_altered',
                                                    'termqualif__historical_annotation',
                                            ).distinct()

            # Informacoes para log
            # Registro
            # ID do model
            id_ctype_identifierqualif = ContentType.objects.filter(model='identifierqualif').values('id')
            context['id_ctype_identifierqualif'] = id_ctype_identifierqualif[0].get('id')
            # ID do registro
            id_identifierqualif = IdentifierQualif.objects.filter(id=id_concept).values('id')
            context['id_identifierqualif'] = id_identifierqualif[0].get('id')

            context['choiced_thesaurus_name'] = Thesaurus.objects.filter(id=self.request.GET.get("ths"))

            return context


