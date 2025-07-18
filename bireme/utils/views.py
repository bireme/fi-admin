from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.utils.translation import ugettext as _
from django.shortcuts import render, render_to_response
from deform.exception import ValidationFailure

from main.decorators import *
from pkg_resources import resource_filename

import csv
import colander
import requests
import deform
import json
import urllib

import sys,traceback

def cookie_lang(request):

    language = request.GET.get('language')
    request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = language
    request.session[settings.LANGUAGE_COOKIE_NAME] = language

    response = HttpResponse(language)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

    return response


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class LoginRequiredView(object):
    """
    Wrap method decorator login_required to use on generic class views
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)

class SuperUserRequiredView(object):
    """
    Wrap method decorator superuser_permission to use on generic class views
    """

    @method_decorator(superuser_permission)
    def dispatch(self, *args, **kwargs):
        return super(SuperUserRequiredView, self).dispatch(*args, **kwargs)


class GenericUpdateWithOneFormset(LoginRequiredView):
    """
    Handle creation and update of objects with one formset (ex. object/translations)
    """

    def form_valid(self, form):
        context = self.get_context_data()
        formset = self.formset(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form,
                                                            formset=formset))

    def form_invalid(self, form):
            # force use of form_valid method to run all validations
            return self.form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(GenericUpdateWithOneFormset, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            context['formset'] = self.formset(instance=self.object)

        return context

class CSVResponseMixin(object):
    """
    A generic mixin that constructs a CSV response from the context data if
    the CSV export option was provided in the request.
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        # Sniff if we need to return a CSV export
        if 'csv' in self.request.GET.get('export', ''):
            data = context['report_rows']
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="%s.csv"' % slugify(context['title'])

            writer = csv.writer(response)
            # Write CSV header line
            writer.writerow(data[0].keys())

            # Write the data from the context somehow
            for item in data:
                encode_values = [value for value in item.values()]
                writer.writerow(encode_values)

            return response
        # Business as usual otherwise
        else:
            return super(CSVResponseMixin, self).render_to_response(context, **response_kwargs)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

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
    # prevent null value
    field_value = field_value if field_value != 'null' else ''

    field_id = request.POST.get('field_id', field_name)
    module_name = request.POST.get('module_name', '')

    formid = request.POST.get('__formid__', '')

    field_name_camelcase = field_name.title().replace('_', '')
    field_full_classname = '{0}.field_definitions.{1}'.format(module_name, field_name_camelcase)

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
        controls = urllib.parse.parse_qsl(str(request.body), keep_blank_values=True)
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
            # convert to json
            field_value_json = json.loads(field_value)
            # check if conversion result in list (OK) otherwise try to fix
            if type(field_value_json) != list:
                # check if original value is code as string
                if field_value.startswith('"'):
                    # remove first and last " of string
                    field_value = field_value[1:-1]
                # unescape string
                field_value = field_value.replace('\\"','"').replace('\\r\\n', '\r\n')
                # convert again
                field_value_json = json.loads(field_value)

            appstruct = {}
            appstruct['data'] = field_value_json

            rendered = form.render(appstruct)
        else:
            # new reference
            rendered = form.render()

    deform_dependencies = form.get_widget_resources()
    deform_dependencies['js'] = [file.replace('deform:static','deform') for file in deform_dependencies['js']]
    deform_dependencies['css'] = [file.replace('deform:static','deform') for file in deform_dependencies['css']]

    return render(request, 'utils/field_assist.html', {
        'form': rendered,
        'field_json': field_json,
        'field_name': field_name,
        'field_id': field_id,
        'module_name': module_name,
        'deform_dependencies': deform_dependencies
    })

@csrf_exempt
def decs_suggestion(request):
    text_to_analyze = request.POST.get('text_to_analyze')
    output_lang = request.POST.get('output_lang')
    text_by_lang = {}
    decs_list = []
    decs_list_unique = []
    decs_ids = []

    text_to_analyze_json = json.loads(text_to_analyze)

    for text in text_to_analyze_json:
        if text and '_i' in text:
            lang = str(text['_i'])
            # concat texts of the same language
            text_by_lang[lang] = text_by_lang.get(lang, '') + ' ' + text['text']

    service_url = settings.DECS_HIGHLIGHTER_URL

    headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'apikey': settings.DECS_HIGHLIGHTER_APIKEY
        }

    for lang, text in text_by_lang.items():
        service_params = {'document': text, 'scanLang': lang, 'pubType': 'h', 'outLang': output_lang}

        r = requests.post(service_url, data=service_params, headers=headers)
        if r.status_code == 200:
            response_json = r.json()
            decs_list_response = response_json['positions']

            for decs_term in decs_list_response:
                decs_id = str(int(decs_term['decsId']))
                if decs_id not in decs_ids:
                    decs_ids.append(decs_id)
                    decs_list_unique.append(decs_term)


    # sort final list
    decs_list = sorted(decs_list_unique, key=lambda k: k['descriptor'])

    return render_to_response('utils/decs_suggestion.html',
                              {'decs_list': decs_list})


@csrf_exempt
def annif_suggestion(request):
    text_to_analyze = request.POST.get('text_to_analyze')
    output_lang = request.POST.get('output_lang')
    text_by_lang = {}
    text_to_analyze_out_lang = {}
    decs_list = []

    try:
        text_to_analyze_json = json.loads(text_to_analyze)
    except json.JSONDecodeError:
        text_to_analyze_json = []

    for text in text_to_analyze_json:
        if text and '_i' in text:
            lang = str(text['_i'])
            # concat texts of the same language
            text_by_lang[lang] = text_by_lang.get(lang, '') + ' ' + text['text']

    # pick only one language to analyze (prefered the same of the output, otherwise the first)
    if output_lang in text_by_lang:
        text_to_analyze_out_lang[output_lang] = text_by_lang[output_lang]
    else:
        first_key = next(iter(text_by_lang))
        text_to_analyze_out_lang[first_key] = text_by_lang[first_key]

    if text_to_analyze_out_lang:
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

        # create params to the request for annif api
        request_lang, request_text = next(iter(text_to_analyze_out_lang.items()))    # lang = 'pt' / text = the content string

        service_url = "{}projects/ensemble-decs-{}/suggest".format(settings.ANNIF_API_URL, request_lang)
        service_params = {'text': request_text, 'language': request_lang, 'limit': 20}

        r = requests.post(service_url, data=service_params, headers=headers)
        if r.status_code == 200:
            response_json = r.json()
            result_response = response_json['results']

            for result in result_response:
                decs_id_list = result['notation'].split('|')  # e.g. D008289|8463
                decs_id = decs_id_list[1] # get ID used by FI-ADMIN (after |)

                decs_detail = {}
                decs_detail['decsId'] = decs_id
                decs_detail['descriptor'] = result['label']
                decs_list.append(decs_detail)

    return render_to_response('utils/decs_suggestion.html',
                              {'decs_list': decs_list})


def custom_page_not_found(request, *args, **argv):
    response = render(request, '404.html', {})

    response.status_code = 404
    return response


def custom_error_page(request, *args, **argv):
    error_type, error_value, tb = sys.exc_info()

    response = render(request, '500.html', {'error_type': error_type,
                                            'error_value': error_value,
                                            'traceback': traceback.format_exception(error_type, error_value, tb)})

    response.status_code = 500
    return response