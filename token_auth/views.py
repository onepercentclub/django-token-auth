import urllib
from django.http.response import HttpResponseRedirect

from django.views.generic.base import View, TemplateView


class TokenLoginView(View):

    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        link = kwargs.get('link')


        from token_auth.auth.booking import (TokenAuthentication, 
                                             TokenAuthenticationError)
        auth = TokenAuthentication()
        try:
            user, created = auth.authenticate(token)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            request.session.modified = True
        except TokenAuthenticationError, e:
            url = '/token/error?message={0}'.format(e)
            return HttpResponseRedirect(url)

        if link:
            return HttpResponseRedirect("/go/login-with/{0}?{1}".format(user.get_jwt_token(), urllib.quote_plus(link)))

        return HttpResponseRedirect("/go/login-with/{0}".format(user.get_jwt_token()))


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
