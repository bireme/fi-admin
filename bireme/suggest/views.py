#! coding: utf-8
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.models import LogEntry

from django.utils.translation import ugettext_lazy as _
from recaptcha.client import captcha

from django.http import Http404, HttpResponse
from django.template import RequestContext

from django.conf import settings
from datetime import datetime
from models import *
from forms import *


import os

@csrf_exempt
def suggest_resource(request, **kwargs):

    suggest = None
    output = {}
    template = ''
    
    suggest = SuggestResource()
   
    form = SuggestResourceForm(request.POST, instance=suggest)

    # talk to the reCAPTCHA service  
    captcha_response = captcha.submit(  
        request.POST.get('recaptcha_challenge_field'),  
        request.POST.get('recaptcha_response_field'),  
        settings.RECAPTCHA_PRIVATE_KEY,  
        request.META['REMOTE_ADDR'],)  


    if form.is_valid() and captcha_response.is_valid:
        template = 'suggest/thanks.html'
        suggest = form.save()
    else:
        template = 'suggest/invalid-link.html'
        output['form'] = form
        output['captcha_error'] = captcha_response.error_code
        print form.errors
    
    return render_to_response(template, output, context_instance=RequestContext(request))

