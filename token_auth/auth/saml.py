from onelogin.saml2.auth import OneLogin_Saml2_Auth

from token_auth.exceptions import TokenAuthenticationError
from token_auth.auth.base import BaseTokenAuthentication


def get_saml_request(request):
    http_host = request.META.get('HTTP_HOST', None)
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        # This is only true for my particular installations.
        server_port = None
        https = request.META.get('HTTP_X_FORWARDED_PROTO') == 'https'
    else:
        server_port = request.META.get('SERVER_PORT')
        https = request.is_secure()

    saml_request = {
        'https': 'on' if https else 'off',
        'http_host': http_host,
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }

    if server_port:
        # Empty port will make a (lonely) colon ':' appear on the URL, so
        # it's better not to include it at all.
        saml_request['server_port'] = server_port

    return saml_request


class SAMLAuthentication(BaseTokenAuthentication):

    def __init__(self, request, **kwargs):
        super(SAMLAuthentication, self).__init__(request, **kwargs)
        self.auth = OneLogin_Saml2_Auth(get_saml_request(request), self.settings)

    def sso_url(self):
        return self.auth.login()

    def parse_user(self, user_data):
        return {
            'email': user_data['User.email'][0],
            'first_name': user_data['User.FirstName'][0],
            'last_name': user_data['User.LastName'][0]
        }

    def authenticate_request(self):

        self.auth.process_response()

        if self.auth.is_authenticated():
            user_data = self.auth.get_attributes()

            return self.parse_user(user_data)
        else:
            raise TokenAuthenticationError(self.auth.get_errors())
