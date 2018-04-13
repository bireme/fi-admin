#! coding: utf-8

from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.contenttypes.models import ContentType

from utils.views import ACTIONS
from django.views import generic
from utils.views import LoginRequiredView, SuperUserRequiredView, GenericUpdateWithOneFormset

from django.conf import settings

from models import *
from forms import *

from django.db.models import Prefetch

from django.utils.translation import ugettext_lazy as _, get_language
from django.core.paginator import Paginator



# Descriptors ------------------------------------------------------------------------

class DescUpdate(LoginRequiredView):
    """
    Handle creation and update of Descriptors objects
    """
    model = IdentifierDesc
    success_url = reverse_lazy('list_descriptor')
    form_class = IdentifierDescForm
    template_name = "thesaurus/descriptor_form.html"

    def form_valid(self, form):
        formset_descriptor = DescriptionDescFormSet(self.request.POST, instance=self.object)
        formset_category = TreeNumbersListDescFormSet(self.request.POST, instance=self.object)
        formset_concept = ConceptListDescFormSet(self.request.POST, instance=self.object)
        # formset_concept_relation = ConceptRelationDescFormSet(self.request.POST, instance=self.object)
        formset_previous = PreviousIndexingListDescFormSet(self.request.POST, instance=self.object)        
        formset_term = TermListDescFormSet(self.request.POST, instance=self.object)

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_category_valid = formset_category.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        # formset_concept_relation_valid = formset_concept_relation.is_valid()
        formset_previous_valid = formset_previous.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_descriptor_valid and formset_category_valid and formset_concept_valid and formset_previous_valid and formset_term_valid):
        # if (form_valid and formset_descriptor_valid and formset_category_valid and formset_concept_valid and formset_concept_relation_valid and formset_previous_valid and formset_term_valid):

            self.object = form.save()

            formset_descriptor.instance = self.object
            formset_descriptor.save()

            formset_category.instance = self.object
            formset_category.save()

            formset_concept.instance = self.object
            formset_concept.save()

            # formset_concept_relation.instance = self.object
            # formset_concept_relation.save()

            formset_previous.instance = self.object
            formset_previous.save()

            formset_term.instance = self.object
            formset_term.save()

            form.save()
            # form.save_m2m()
            return HttpResponseRedirect(self.get_success_url())

        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_category=formset_category,
                                            formset_concept=formset_concept,
                                            formset_previous=formset_previous,
                                            formset_term=formset_term
                                            )
                                        )

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(DescUpdate, self).get_context_data(**kwargs)

        context['descriptor_info'] = get_language()

        if IdentifierDesc.objects.count() > 0:
            context['next_id'] = int(IdentifierDesc.objects.latest('id').id) + 60000
        else:
            context['next_id'] = 1


        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionDescFormSet(instance=self.object)
            context['formset_category'] = TreeNumbersListDescFormSet(instance=self.object)
            context['formset_concept'] = ConceptListDescFormSet(instance=self.object)

            # context['formset_concept_relation'] = ConceptRelationDescFormSet(instance=self.object)

            context['formset_previous'] = PreviousIndexingListDescFormSet(instance=self.object)
            context['formset_term'] = TermListDescFormSet(instance=self.object)

       
        return context



class DescUpdateView(DescUpdate, UpdateView):
    """
    Used as class view to update Descriptors
    Extend DescUpdate that do all the workTemefos
    """


class DescCreateView(DescUpdate, CreateView):
    """
    Used as class view to create Descriptors
    Extend DescUpdate that do all the work
    """


class DescDeleteView(DescUpdate, DeleteView):
    """
    Used as class view to delete Descriptors
    Extend DescUpdate that do all the work
    """
    model = IdentifierDesc
    template_name = 'thesaurus/descriptor_confirm_delete.html'
    success_url = reverse_lazy('list_descriptor')


class DescListView(LoginRequiredView, ListView):
    """
    List descriptor records (used by relationship popup selection window)
    """
    template_name = "thesaurus/thesaurus_home.html"
    context_object_name = "registers"
    paginate_by = settings.ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        param_descriptor_name = self.request.GET.get('descriptor_name')
        param_descriptor_ui = self.request.GET.get('descriptor_ui')
        param_decs_code = self.request.GET.get('decs_code')
        object_list = []

        if param_descriptor_name:
            object_list = IdentifierDesc.objects.filter(
                descriptors__descriptor_name__icontains=param_descriptor_name,
                descriptors__language_code=lang_code
            ).values('id','descriptor_ui','decs_code','descriptors__descriptor_name')

        else:
            object_list = IdentifierDesc.objects.prefetch_related(
                Prefetch(
                    "descriptors",
                    # queryset=DescriptionDesc.objects.filter(language_code=lang_code),
                    queryset=DescriptionDesc.objects.filter(),
                    to_attr="descriptor_name",
                )
            )

        return object_list


# class DescConceptRelationView(LoginRequiredView, FormView):
#     """
#     Handle creation and update of Concept List Descriptors objects
#     """
#     success_url = reverse_lazy('list_descriptor')
#     form_class = ConceptRelationDescForm
#     template_name = "thesaurus/edit_concept_relation_descriptor_form.html"




# Qualifiers -------------------------------------------------------------------------
class QualifUpdate(LoginRequiredView):
    """
    Handle creation and update of Qaulifier objects
    """
    model = IdentifierQualif
    success_url = reverse_lazy('list_qualifier')
    form_class = IdentifierQualifForm
    template_name = "thesaurus/qualifier_form.html"

    def dispatch(self, *args, **kwargs):
        return super(QualifUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        formset_descriptor = DescriptionQualifFormSet(self.request.POST, instance=self.object)
        formset_category = TreeNumbersListQualifFormSet(self.request.POST, instance=self.object)
        formset_concept = ConceptListQualifFormSet(self.request.POST, instance=self.object)
        formset_term = TermListQualifFormSet(self.request.POST, instance=self.object)        

        # run all validation before for display formset errors at form
        form_valid = form.is_valid()
        formset_descriptor_valid = formset_descriptor.is_valid()
        formset_category_valid = formset_category.is_valid()
        formset_concept_valid = formset_concept.is_valid()
        formset_term_valid = formset_term.is_valid()

        if (form_valid and formset_descriptor_valid and formset_concept_valid and formset_category_valid and formset_term_valid):
            self.object = form.save()

            formset_descriptor.instance = self.object
            formset_descriptor.save()

            formset_category.instance = self.object
            formset_category.save()

            formset_concept.instance = self.object
            formset_concept.save()

            formset_term.instance = self.object
            formset_term.save()

            form.save()
            return HttpResponseRedirect(self.get_success_url())

        else:
            return self.render_to_response(
                        self.get_context_data(
                                            form=form,
                                            formset_descriptor=formset_descriptor,
                                            formset_category=formset_category,
                                            formset_concept=formset_concept,
                                            formset_term=formset_term
                                            )
                                        )

    def form_invalid(self, form):
        # force use of form_valid method to run all validations
        return self.form_valid(form)


    def get_context_data(self, **kwargs):
        context = super(QualifUpdate, self).get_context_data(**kwargs)

        if self.request.method == 'GET':

            context['formset_descriptor'] = DescriptionQualifFormSet(instance=self.object)
            context['formset_category'] = TreeNumbersListQualifFormSet(instance=self.object)
            context['formset_concept'] = ConceptListQualifFormSet(instance=self.object)
            context['formset_term'] = TermListQualifFormSet(instance=self.object)

            context['qualifier_info'] = get_language()

        return context


class QualifCreateView(QualifUpdate, CreateView):
    """
    Used as class view to create Qualifiers
    Extend QualifUpdate that do all the work
    """


class QualifUpdateView(QualifUpdate, UpdateView):
    """
    Used as class view to update Qualifiers
    Extend QualifUpdate that do all the work
    """


class QualifDeleteView(QualifUpdate, DeleteView):
    """
    Used as class view to delete Qualifiers
    Extend QualifUpdate that do all the work
    """
    model = IdentifierQualif
    template_name = 'thesaurus/qualifier_confirm_delete.html'
    success_url = reverse_lazy('list_qualifier')


class QualifListView(LoginRequiredView, ListView):
    """
    List qualifier records (used by relationship popup selection window)
    """
    template_name = "thesaurus/qualifier_list.html"
    context_object_name = "registers"
    paginate_by = settings.ITEMS_PER_PAGE

    def get_queryset(self):
        lang_code = get_language()
        param_descriptor_name = self.request.GET.get('descriptor_name')
        param_descriptor_ui = self.request.GET.get('descriptor_ui')
        param_decs_code = self.request.GET.get('decs_code')
        object_list = []

        if param_descriptor_name:
            object_list = IdentifierQualif.objects.filter(
                qualifiers__qualifier_name__icontains=param_descriptor_name,
                qualifiers__language_code=lang_code
            ).values('id','qualifier_ui','decs_code','qualifiers__qualifier_name')

        else:
            object_list = IdentifierQualif.objects.prefetch_related(
                Prefetch(
                    "qualifiers",
                    # queryset=DescriptionQualif.objects.filter(language_code=lang_code),
                    queryset=DescriptionQualif.objects.filter(),
                    to_attr="qualifier_name",
                )
            )

        return object_list
