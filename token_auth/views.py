import urllib
import json

from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic.base import View, TemplateView, RedirectView
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


class TokenRedirectView(RedirectView):
    """
    Redirect to SSO login page
    """

    permanent = False
    query_string = True
    pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        auth = get_auth(self.request, **kwargs)
        sso_url = auth.sso_url()
        return sso_url


class TokenLoginView(View):

    def parse_request(self, request, *args, **kwargs):
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

    def get(self, request, *args, **kwargs):
        return self.parse_request(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.parse_request(request, *args, **kwargs)


class TokenLogoutView(TemplateView):
    """
    Process Single Logout
    FIXME: Not working yet
    """

    query_string = True
    template_name = 'token/token-logout.tpl'

    def get(self, request, *args, **kwargs):
        link = kwargs.get('link')
        auth = get_auth(request, **kwargs)
        dscb = lambda: request.session.flush()
        url = auth.process_slo(delete_session_cb=dscb)
        errors = auth.auth.get_errors()
        if len(errors) == 0:
            if url is not None:
                return HttpResponseRedirect(url)
            else:
                success_slo = True
        print errors
        return self.render_to_response(errors)


class TokenErrorView(TemplateView):

    query_string = True
    template_name = 'token/token-error.tpl'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['message'] = request.GET.get('message', 'Unknown')
        auth = get_auth(request, **kwargs)
        context['ssoUrl'] = auth.sso_url()
        return self.render_to_response(context)


class MembersOnlyView(TemplateView):

    query_string = True
    template_name = 'token/members-only.tpl'

    def get(self, request, *args, **kwargs):
        auth = get_auth(request, **kwargs)
        context = self.get_context_data(**kwargs)
        context['url'] = request.GET.get('url', '')
        context['ssoUrl'] = auth.sso_url()
        return self.render_to_response(context)


class MetadataView(TemplateView):
    """
    Show (SAML) metadata
    FIXME: Make this dynamic
    """
    template_name = 'token/metadata.tpl'
