from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.forms.utils import ErrorList

from django.contrib.contenttypes.generic import BaseGenericInlineFormSet

class SpanWidget(forms.Widget):
    '''Renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe(u'<span%s >%s</span>' % (
            forms.util.flatatt(final_attrs), self.original_value))

    def value_from_datadict(self, data, files, name):
        return self.original_value

class SpanField(forms.Field):
    '''A field which renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', SpanWidget)
        super(SpanField, self).__init__(*args, **kwargs)

class Readonly(object):
    '''Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    '''

    class NewMeta:
        readonly = tuple()

    def __init__(self, *args, **kwargs):
        super(Readonly, self).__init__(*args, **kwargs)
        readonly = self.NewMeta.readonly
        if not readonly:
            return
        for name, field in self.fields.items():
            if name in readonly:
                field.widget = SpanWidget()
            elif not isinstance(field, SpanField):
                continue
            field.widget.original_value = str(getattr(self.instance, name))

class ReadonlyForm(Readonly, forms.Form):
    '''A form which provides the ability to specify certain fields as
    readonly, meaning that they will display their value as text wrapped
    with a <span> tag. The user is unable to edit them, and they are
    protected from POST data insertion attacks.

    The recommended usage is to place a NewMeta inner class on the
    form, with a readonly attribute which is a list or tuple of fields,
    similar to the fields and exclude attributes on the Meta inner class.

        class MyForm(ReadonlyForm):
            foo = forms.TextField()
            class NewMeta:
                readonly = ('foo',)
    '''
    pass

class ReadonlyModelForm(Readonly, forms.ModelForm):
    '''A ModelForm which provides the ability to specify certain fields as
    readonly, meaning that they will display their value as text wrapped
    with a <span> tag. The user is unable to edit them, and they are
    protected from POST data insertion attacks.

    The recommended usage is to place a NewMeta inner class on the
    form, with a readonly attribute which is a list or tuple of fields,
    similar to the fields and exclude attributes on the Meta inner class.

        class Foo(models.Model):
            bar = models.CharField(max_length=24)

        class MyForm(ReadonlyModelForm):
            class Meta:
                model = Foo
            class NewMeta:
                readonly = ('bar',)
    '''
    pass


class DisableableSelectWidget(forms.Select):
    def __init__(self, attrs=None, disabled_choices=(), choices=()):
        super(DisableableSelectWidget, self).__init__(attrs, choices)
        self.disabled_choices = list(disabled_choices)

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        if option_value in self.disabled_choices:
            disabled_html = u' disabled="disabled"'
        else:
            disabled_html = ''
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))


class DescriptorRequired(BaseGenericInlineFormSet):
    class Meta:
        fields = '__all__'

    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data and form.cleaned_data.get('DELETE') == False:
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError( _('You must have at least one descriptor'), code='invalid')


class ResourceThematicRequired(BaseGenericInlineFormSet):
    class Meta:
        fields = '__all__'

    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data and form.cleaned_data.get('DELETE') == False:
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError( _('You must have at least one thematic area'), code='invalid')



def is_valid_for_publication(form, formsets):
    """
    Before admit a resources/events check if they have at least one admitted descriptors and at least
    one thematic area.
    """
    #Do cross validation on forms
    valid = True
    descriptor_admitted = False
    thematic_admitted = False
    data = None

    if hasattr(form, 'cleaned_data'):
        status = form.cleaned_data.get("status")
        form_class = type(form).__name__
        '''
        For status = admitted check if the resource have at least
        one descriptor and one thematica area
        '''
        if status == 1:
            #for biblioref descriptor/thematic status is admited by default
            status_default = True if 'BiblioRef' in form_class else False

            # access forms from formsets:
            for formset in formsets:
                for formset_form in formset.forms:
                    if hasattr(formset_form, 'cleaned_data'):
                        data = formset_form.cleaned_data

                        # check for status and not marked for DELETE
                        if data.get('status', status_default) == 1 and data.get('DELETE') == False:
                            if data.get('text') and data.get('code'):
                                descriptor_admitted = True

                            elif data.get('thematic_area'):
                                thematic_admitted = True


            if not descriptor_admitted:
                # For publication must have at least one descriptor admitted
                valid = False

            if not thematic_admitted:
                # For publication must have at least one thematic area admitted
                valid = False

            if not valid:
                form.non_field_errors = ErrorList([_('For status "Published" you must have at least one descriptor and one thematic area')])

    return valid
