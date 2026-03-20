from django.urls import re_path

from thesaurus.views import *

urlpatterns = [

    # Descriptors -------------------------------------------------------------------------------------------
    re_path(r'^descriptors/?$', DescListView.as_view(), name='list_descriptor'),

    # Pagina de redirecionamento para criação de novo registro a partir de um TERMO existente
    re_path(r'^descriptors/create/term/confirm/?$', TermCreateDescConfirm.as_view(), name='create_confirm_termdesc'),
    re_path(r'^descriptors/create/term/do/(?P<ths>\d+)/?$', TermCreateDescDo, name='do_create_termdesc'),

    # Pagina de redirecionamento para criação de novo registro a partir de um CONCEITO existente
    re_path(r'^descriptors/create/concept/confirm/?$', ConceptCreateDescConfirm.as_view(), name='create_confirm_conceptdesc'),
    re_path(r'^descriptors/create/concept/do/(?P<ths>\d+)/?$', ConceptCreateDescDo, name='do_create_conceptdesc'),

    # Form 0 para pesquisa de existencia de termo - Se não existir segue Form1
    re_path(r'^descriptors/chk/?$', TermListDescChk.as_view(), name='chk_termdesc'),

    # Form 1 para criacao de novo registro
    re_path(r'^descriptors/new/?$', DescCreateView.as_view(), name='create_descriptor'),

    # Form 2 para criacao de novo registro
    re_path(r'^descriptors/register/term/?$', DescCreateView2.as_view(), name='create_concept_termdesc'),

    # Delecao caso seja cancelado a inclusao de novo registro, a partir do Form2
    re_path(r'^descriptors/delete/(?P<pk>\d+)/?$', DescDeleteView.as_view(), name='delete_descriptor'),

    # PageViewDesc - lista registro - Abas Details e Concepts
    re_path(r'^descriptors/view/(?P<pk>[\w-]+)$', PageViewDesc.as_view(), name='detail_descriptor'),

    # Edit Register
    re_path(r'^descriptors/register/edit/(?P<pk>\d+)/?$', DescRegisterUpdateView.as_view(), name='edit_register_desc'),

    # Cria conceito + Termo
    re_path(r'^descriptors/concept/new/?$', ConceptListDescCreateView.as_view(), name='create_concept_desc'),
    re_path(r'^descriptors/concept/edit/(?P<pk>\d+)/?$', ConceptListDescUpdateView.as_view(), name='edit_concept_desc'),

    # Cria Termo
    re_path(r'^descriptors/term/new/?$', TermListDescCreateView.as_view(), name='create_term_desc'),
    re_path(r'^descriptors/term/edit/(?P<pk>\d+)/?$', TermListDescUpdateView.as_view(), name='edit_term_desc'),

    # Cria Edita Legado
    re_path(r'^descriptors/legacy/new/?$', legacyInformationDescCreateView.as_view(), name='create_legacy_desc'),
    re_path(r'^descriptors/legacy/edit/(?P<pk>\d+)/?$', legacyInformationDescUpdateView.as_view(), name='edit_legacy_desc'),

    # Referente a migracao de conceito
    re_path(r'^descriptors/concept/?$', ConceptListDescView.as_view(), name='list_concept'),
    re_path(r'^descriptors/concept/move/(?P<term_id>\d+)/(?P<ths>\d+)/(?P<concept_ori>\d+)?$', ConceptListDescModification, name='move_concept_desc'),

    # Referente a migracao de termo
    re_path(r'^descriptors/term/?$', TermListDescView.as_view(), name='list_term'),
    re_path(r'^descriptors/term/move/(?P<term_id>\d+)/(?P<ths>\d+)/(?P<term_ori>\d+)?$', TermListDescModification, name='move_term_desc'),


    # Qualifiers --------------------------------------------------------------------------------------------
    re_path(r'^qualifiers/?$', QualifListView.as_view(), name='list_qualifier'),

    # Pagina de redirecionamento para criação de novo registro a partir de um TERMO existente
    re_path(r'^qualifiers/create/term/confirm/?$', TermCreateQualifConfirm.as_view(), name='create_confirm_termqualif'),
    re_path(r'^qualifiers/create/term/do/(?P<ths>\d+)/?$', TermCreateQualifDo, name='do_create_termqualif'),

    # Pagina de redirecionamento para criação de novo registro a partir de um CONCEITO existente
    re_path(r'^qualifiers/create/concept/confirm/?$', ConceptCreateQualifConfirm.as_view(), name='create_confirm_conceptqualif'),

    # Form 0 para pesquisa de existencia de qualificador - Se não existir segue Form1
    re_path(r'^qualifiers/chk/?$', QualifListDescChk.as_view(), name='chk_termqualif'),

    # Form 1 para criacao de novo registro
    re_path(r'^qualifiers/new/?$', QualifCreateView.as_view(), name='create_qualifier'),

    # Form 2 para criacao de novo registro
    re_path(r'^qualifiers/register/term/?$', QualifCreateView2.as_view(), name='create_concept_termqualif'),

    # Delecao caso seja cancelado a inclusao de novo registro, a partir do Form2
    re_path(r'^qualifiers/delete/(?P<pk>\d+)/?$', QualifDeleteView.as_view(), name='delete_qualifier'),

    # PageViewQualif - lista registro - Abas Details e Concepts
    re_path(r'^qualifiers/view/(?P<pk>[\w-]+)$', PageViewQualif.as_view(), name='detail_qualifier'),

    # Edit Register
    re_path(r'^qualifiers/register/edit/(?P<pk>\d+)/?$', QualifRegisterUpdateView.as_view(), name='edit_register_qualif'),

    # Cria conceito + Termo
    re_path(r'^qualifiers/concept/new/?$', ConceptListQualifCreateView.as_view(), name='create_concept_qualif'),
    re_path(r'^qualifiers/concept/edit/(?P<pk>\d+)/?$', ConceptListQualifUpdateView.as_view(), name='edit_concept_qualif'),

    # Cria Termo
    re_path(r'^qualifiers/term/new/?$', TermListQualifCreateView.as_view(), name='create_term_qualif'),
    re_path(r'^qualifiers/term/edit/(?P<pk>\d+)/?$', TermListQualifUpdateView.as_view(), name='edit_term_qualif'),

    # Cria Edita Legado
    re_path(r'^qualifiers/legacy/new/?$', legacyInformationQualifCreateView.as_view(), name='create_legacy_qualif'),
    re_path(r'^qualifiers/legacy/edit/(?P<pk>\d+)/?$', legacyInformationQualifUpdateView.as_view(), name='edit_legacy_qualif'),

    # Referente a migracao de conceito
    re_path(r'^qualifiers/concept/?$', ConceptListQualifView.as_view(), name='list_concept_qualif'),
    re_path(r'^qualifiers/concept/move/(?P<term_id>\d+)/(?P<ths>\d+)/(?P<concept_ori>\d+)?$', ConceptListQualifModification, name='move_concept_qualif'),

    # Referente a migracao de termo
    re_path(r'^qualifiers/term/?$', TermListQualifView.as_view(), name='list_qualif'),
    re_path(r'^qualifiers/term/move/(?P<term_id>\d+)/(?P<ths>\d+)/(?P<term_ori>\d+)?$', TermListQualifModification, name='move_term_qualif'),

]
