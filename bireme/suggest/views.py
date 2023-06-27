#! coding: utf-8
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry

from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from django.http import Http404, HttpResponse
from django.template import RequestContext

from utils.context_processors import additional_user_info

from django.conf import settings
from datetime import datetime
from main.models import Resource, Keyword
from events.models import Event

from suggest.models import *
from suggest.forms import *

from django.db.models import Q

import os
import json
import urllib

@csrf_exempt
def suggest_resource(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    captcha_is_valid = True
    captcha_error = ''

    suggest = SuggestResource()

    form = ExternalSuggestResourceForm(request.POST, instance=suggest)

    if settings.RECAPTCHA_PRIVATE_KEY:
        # Check the captcha with reCAPTCHA (google service)
        captcha_response = validate_recaptcha(
            settings.RECAPTCHA_PRIVATE_KEY,
            request.POST.get('g-recaptcha-response'),
            request.META['REMOTE_ADDR'],)

        if not captcha_response['is_valid']:
            # captcha is wrong show a error message in the template.
            captcha_is_valid = False
            captcha_error = captcha_response['error_code']

    if form.is_valid() and captcha_is_valid:
        template = 'suggest/thanks.html'
        suggest = form.save()
    else:
        template = 'suggest/invalid-link.html'
        output['form'] = form
        output['captcha_error'] = captcha_error

    return render(request, template, output)

@login_required
def list_suggestions(request):

    user = request.user
    output = {}
    delete_id = request.POST.get('delete_id')
    suggestions = None

    if delete_id:
        delete_resource(request, delete_id)

    # getting action parameters
    actions = {}
    for key in settings.ACTIONS.keys():
        if request.GET.get(key):
            actions[key] = request.GET.get(key)
        else:
            actions[key] = settings.ACTIONS[key]

    page = 1
    if actions['page'] and actions['page'] != '':
        page = actions['page']

    if actions['type'] and actions['type'] == 'keywords':
        suggestions = Keyword.objects.filter(user_recomendation=True, status=0, text__icontains=actions['s'])
    elif actions['type'] == 'events':
        suggestions = SuggestEvent.objects.filter(Q(title__icontains=actions['s']) | Q(origin__icontains=actions['s']))
    else:
        suggestions = SuggestResource.objects.filter(title__icontains=actions['s'])


    if not actions['filter_status']:
        actions['filter_status'] = '0'

    if actions['filter_status'] != '*':
        suggestions = suggestions.filter(status=actions['filter_status'])


    suggestions = suggestions.order_by(actions["orderby"])
    if actions['order'] == "-":
        suggestions = suggestions.order_by("%s%s" % (actions["order"], actions["orderby"]))

    # pagination
    pagination = {}
    paginator = Paginator(suggestions, settings.ITEMS_PER_PAGE)
    pagination['paginator'] = paginator
    pagination['page'] = paginator.page(page)
    suggestions = pagination['page'].object_list

    output['suggestions'] = suggestions
    output['actions'] = actions
    output['pagination'] = pagination

    return render(request, 'suggest/list.html', output)

@login_required
def edit_suggested_resource(request, **kwargs):

    resource_id = kwargs.get('resource_id')
    resource = None
    form = None
    output = {}

    resource = get_object_or_404(SuggestResource, id=resource_id)

    # save/update
    if request.POST:
        form = SuggestResourceForm(request.POST, request.FILES, instance=resource)

        if form.is_valid():
            resource = form.save()

            output['alert'] = _("Resource successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('suggest.views.list_suggestions')
    # new/edit
    else:
        form = SuggestResourceForm(instance=resource)

    output['form'] = form
    output['resource'] = resource
    output['settings'] = settings

    return render(request, 'suggest/edit-suggested-resource.html', output)


@login_required
def create_resource_from_suggestion(request, suggestion_id):

    user = request.user
    suggestion = get_object_or_404(SuggestResource, id=suggestion_id)
    output = {}

    user_data = additional_user_info(request)

    resource = Resource(title=suggestion.title, link=suggestion.link,
        abstract=suggestion.abstract, created_by=request.user)
    resource.save();

    for tag in suggestion.keywords.split(','):
            keyword = Keyword(content_object=resource, text=tag.strip(), user_recomendation=True)
            keyword.save()

    suggestion.status = 1
    suggestion.save();

    output['alert'] = _("Resource created.")
    output['alerttype'] = "alert-success"

    return redirect('main:edit_resource', resource_id=resource.id)


@login_required
def create_event_from_suggestion(request, suggestion_id):

    user = request.user
    suggestion = get_object_or_404(SuggestEvent, id=suggestion_id)
    output = {}

    user_data = additional_user_info(request)

    event = Event(title=suggestion.title, start_date=suggestion.start_date,
        end_date=suggestion.end_date, link=suggestion.link, city=suggestion.city, created_by=request.user)
    event.save();

    suggestion.status = 1
    suggestion.save();

    output['alert'] = _("Event created.")
    output['alerttype'] = "alert-success"

    return redirect('events:edit_event', event_id=event.id)


@csrf_exempt
def suggest_tag(request, **kwargs):

    resource = None
    response = None
    sucess = True

    resource_id = escape(request.POST.get('resource_id'))
    suggest_tag = escape(request.POST.get('tags'))

    try:
        resource = Resource.objects.get(pk=resource_id)
    except Resource.DoesNotExist:
        sucess = False

    if resource != None:
        for tag in suggest_tag.split(','):
            keyword = Keyword(content_object=resource, text=tag.strip(), user_recomendation=True)
            keyword.save()


    response = HttpResponse(sucess)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST"
    response["Access-Control-Allow-Headers"] = "*"

    return response


@csrf_exempt
def suggest_event(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    captcha_is_valid = True
    captcha_error = ''

    suggest = SuggestEvent()

    form = ExternalSuggestEventForm(request.POST, instance=suggest)

    if settings.RECAPTCHA_PRIVATE_KEY:
        # Check the captcha with reCAPTCHA (google service)
        captcha_response = validate_recaptcha(
            settings.RECAPTCHA_PRIVATE_KEY,
            request.POST.get('g-recaptcha-response'),
            request.META['REMOTE_ADDR'],)

        if not captcha_response['is_valid']:
            # captcha is wrong show a error message in the template.
            captcha_is_valid = False
            captcha_error = captcha_response['error_code']

    lang_code = request.POST.get('language', 'pt-BR')
    if hasattr(request, 'session'):
        request.session['django_language'] = lang_code
    else:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    if form.is_valid() and captcha_is_valid:
        template = 'suggest/thanks.html'
        suggest = form.save()
        output['type'] = 'event'
    else:
        template = 'suggest/invalid-link.html'
        output['form'] = form
        output['captcha_error'] = captcha_error

    return render(request, template, output)


@login_required
def edit_suggested_event(request, **kwargs):

    suggest_id = kwargs.get('suggest_id')
    suggest = None
    form = None
    output = {}

    suggest = get_object_or_404(SuggestEvent, id=suggest_id)

    # save/update
    if request.POST:
        form = SuggestEventForm(request.POST, request.FILES, instance=suggest)

        if form.is_valid():
            suggest = form.save()

            output['alert'] = _("Event successfully edited.")
            output['alerttype'] = "alert-success"

            return redirect('suggest.views.list_suggestions')
    # new/edit
    else:
        form = SuggestEventForm(instance=suggest)

    output['form'] = form
    output['suggest'] = suggest
    output['settings'] = settings

    return render(request, 'suggest/edit-suggested-event.html', output)


def validate_recaptcha (private_key, recaptcha_response, remoteip):
    """
    Submits a reCAPTCHA request for verification. Returns RecaptchaResponse
    for the request

    private_key -- your reCAPTCHA private key
    recaptcha_response -- The value of recaptcha_response from the form
    remoteip -- the user's ip address
    """
    return_values = {}

    if not (recaptcha_response):
        return {'is_valid': False, 'error_code': 'incorrect-captcha-sol'}

    params = urllib.parse.urlencode ({
                'secret': private_key,
                'remoteip': remoteip,
                'response' : recaptcha_response
            }).encode('utf-8')

    request = urllib.request.Request (
        url = "https://www.google.com/recaptcha/api/siteverify",
        data = params,
        headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'User-agent': 'noReCAPTCHA Python'
          }
        )

    httpresp = urllib.request.urlopen(request)
    try:
        res = httpresp.read()
        return_values = json.loads(res)

    except (ValueError, TypeError):
        return {'is_valid': False, 'error_code': 'json-read-issue'}
    except:
        return {'is_valid': False, 'error_code': 'unknown-network-issue'}
    finally:
        httpresp.close()

    is_valid = return_values.get('success', False)
    error_code = return_values.get('error_code', '')
    return_values = {'is_valid': is_valid, 'error_code': error_code}

    return return_values
