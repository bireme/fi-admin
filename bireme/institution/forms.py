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

class URLForm(forms.ModelForm):
    # add class to field
    url = forms.URLField(widget=widgets.URLInput(attrs={'class': 'input-xlarge'}))

class PersonForm(forms.ModelForm):
    # add class to field
    name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-xlarge'}))

class EmailForm(forms.ModelForm):
    # add class to field
    email_name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-xlarge'}))

class PhoneForm(forms.ModelForm):
    # add class to field
    phone_name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-xlarge'}))
    country_code = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-mini'}))
    phone_number = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-medium'}))


class InstRelatedForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ('status', 'type', 'name', 'acronym', 'country')

    name = forms.CharField(widget=widgets.TextInput(attrs={'class': 'input-xxlarge'}))

    def clean_name(self):
        data = self.cleaned_data.get('name')

        has_inst = Institution.objects.filter(name__iexact=data).exists()
        if has_inst:
            message = _("This institution already exist")
            self.add_error('name', message)        

        return data


# definition of inline formsets
URLFormSet = inlineformset_factory(Institution, URL, form=URLForm,
                                   fields='__all__', can_delete=True, extra=1)

PersonFormSet = inlineformset_factory(Institution, ContactPerson, form=PersonForm,
                                      fields='__all__', can_delete=True, extra=1)

PhoneFormSet = inlineformset_factory(Institution, ContactPhone, form=PhoneForm,
                                     fields='__all__', can_delete=True, extra=1)

EmailFormSet = inlineformset_factory(Institution, ContactEmail, form=EmailForm,
                                     fields='__all__', can_delete=True, extra=1)

RelationFormSet = inlineformset_factory(Institution, Relationship,
                                        fields='__all__', fk_name='institution',
                                        can_delete=True, extra=1)
