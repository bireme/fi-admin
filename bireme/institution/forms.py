from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from django.forms import widgets
from django import forms

from models import *

class InstitutionForm(forms.ModelForm):

    class Meta:
        model  = Institution
        exclude = ('cooperative_center_code', )
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.user_data = kwargs.pop('user_data', None)

        super(InstitutionForm, self).__init__(*args, **kwargs)

        user_cc = self.user_data.get('user_cc', '')
        # only enable edition of cc_code field for BIREME staff
        if user_cc != 'BR1.1':
            self.fields['status'].widget = widgets.HiddenInput()
            self.fields['cc_code'].widget = widgets.HiddenInput()

class URLForm(forms.ModelForm):
    # add class to field
    url = forms.URLField(widget=widgets.URLInput(attrs={'class': 'input-xlarge'}))

class ContactForm(forms.ModelForm):
    # add class to field
    name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-large'}), required=False)
    job_title = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-medium'}), required=False)
    email = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-medium'}), required=False)
    country_area_code = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-mini'}), required=False)


class AdmForm(forms.ModelForm):
    notes = forms.CharField(widget=widgets.Textarea(attrs={'class': 'input-xxlarge'}), required=False)

    class Meta:
        model = Adm
        fields = '__all__'

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name', 'acronym', 'country')

    name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-xxlarge'}))

    def clean_name(self):
        data = self.cleaned_data.get('name')

        has_inst = Unit.objects.filter(name__iexact=data).exists()
        if has_inst:
            message = _("This unit already exist")
            self.add_error('name', message)

        return data


# definition of inline formsets
URLFormSet = inlineformset_factory(Institution, URL, form=URLForm,
                                   fields='__all__', can_delete=True, extra=1)

ContactFormSet = inlineformset_factory(Institution, Contact, form=ContactForm,
                                      fields='__all__', can_delete=True, extra=1)

UnitLevelFormSet = inlineformset_factory(Institution, UnitLevel,
                                         fields='__all__', can_delete=True, extra=1)

AdmFormSet = inlineformset_factory(Institution, Adm, form=AdmForm, extra=1,
                                   max_num=1, can_delete=False)
