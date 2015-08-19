import urllib
import json

from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic.base import View, TemplateView
from django.utils.module_loading import import_by_path
from django.core.exceptions import ImproperlyConfigured

from token_auth.exceptions import TokenAuthenticationError
from token_auth.utils import get_settings


def get_auth(request, **kwargs):
    settings = get_settings()
    try:
        backend = settings['backend']
    except AttributeError:
        raise ImproperlyConfigured('TokenAuth backend not set')

    try:
        cls = import_by_path(backend)
    except AttributeError:
        raise ImproperlyConfigured(
            'TokenAuth backend {} is not defined'.format(backend)
        )
    return cls(request, **kwargs)


class TokenRedirectView(View):
    def get(self, request, *args, **kwargs):
        auth = get_auth(request)

        return HttpResponse(json.dumps({'sso-url': auth.sso_url()}))


class TokenLoginView(View):

    def get(self, request, *args, **kwargs):
        link = kwargs.get('link')
        auth = get_auth(request, **kwargs)

        try:
            user, created = auth.authenticate()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
        except TokenAuthenticationError, e:
            url = '/token/error?message={0}'.format(e)
            return HttpResponseRedirect(url)

        if link:
            return HttpResponseRedirect("/go/login-with/{0}?{1}".format(
                user.get_jwt_token(), urllib.quote_plus(link)))

        return HttpResponseRedirect("/go/login-with/{0}".format(
            user.get_jwt_token()))


class TokenErrorView(TemplateView):

    query_string = True
    template_name = 'token/token-error.tpl'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['message'] = request.GET.get('message', 'Unknown')
        return self.render_to_response(context)


class MembersOnlyView(TemplateView):

    query_string = True
    template_name = 'token/members-only.tpl'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['url'] = request.GET.get('url', '')
        return self.render_to_response(context)
