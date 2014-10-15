from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from main.decorators import *

# form actions
ACTIONS = {
    'orderby': 'id',
    'order': '-',
    'page': 1,
    'type': "",
    's': "",
    'filter_owner': "",
    'filter_status': "",
    'filter_thematic': "",
}

def cookie_lang(request):

    language = request.REQUEST.get('language')
    request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = language
    request.session[settings.LANGUAGE_COOKIE_NAME] = language

    response = HttpResponse(language)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

    return response


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
