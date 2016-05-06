from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.utils import ErrorList
from utils.forms import is_valid_for_publication


def check_url_or_attachment(form, formset_attachment):
    """
    Check if is present the electronic_address field or any attachment
    """
    url_or_attachment = True

    if not form.cleaned_data['electronic_address']:
        count = 0
        for form_attach in formset_attachment:
            try:
                if form_attach.cleaned_data and form_attach.cleaned_data.get('DELETE') == False:
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            url_or_attachment = False
            formset_attachment.non_form_errors = ErrorList([_('Eletronic address or fulltext file required')])
            formset_attachment.is_valid = False

    return url_or_attachment


def check_for_publication(form, formsets, user_data):
    """
    Run additional validation across forms fields for status LILACS-Express and LILACS
    """
    valid = True
    status = form.cleaned_data['status']
    user_role = user_data['service_role'].get('LILDBI')

    # for LILACS status and not Serie Source is required descriptor and thematic area
    if status == 1 and form.document_type != 'S':
        valid = is_valid_for_publication(form, [formsets['descriptor'], formsets['thematic']])

    # for analytic of a serie is required electronic_address or attachment
    if form.document_type == 'Sas' and status != -1:
        # check for electronic_address or attachment present
        valid = check_url_or_attachment(form, formsets['attachment'])


    return valid
