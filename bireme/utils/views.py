from django.http import Http404, HttpResponse
from django.conf import settings

# form actions
ACTIONS = {
    'orderby': 'id',
    'order': '+',
    'page': 1,
    's': "",
    'filter_owner': "",
}

def cookie_lang(request):

    language = request.REQUEST.get('language')
    request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = language
    request.session[settings.LANGUAGE_COOKIE_NAME] = language

    response = HttpResponse(language)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

    return response
