from django.forms import ModelForm


class Fieldset:
    def __init__(self, form, name, fields, legend='', classes='', description=''):
        self.form = form
        self.name = name
        self.fields = fields
        self.legend = legend
        self.classes = classes if isinstance(classes, str) else ' '.join(classes)
        self.description = description

    def __iter__(self):
        for field_name in self.fields:
            if field_name in self.form.fields:
                bound_field = self.form[field_name]
                if not hasattr(bound_field, 'row_attrs'):
                    bound_field.row_attrs = ''
                yield bound_field


class FieldsetCollection:
    def __init__(self, form, fieldsets):
        self.form = form
        self.fieldsets = fieldsets or []

    def __iter__(self):
        for name, options in self.fieldsets:
            yield Fieldset(
                self.form,
                name,
                fields=options.get('fields', []),
                legend=options.get('legend', ''),
                classes=options.get('classes', ''),
                description=options.get('description', ''),
            )


class BetterModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._fieldset_collection = None
        super().__init__(*args, **kwargs)
