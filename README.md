# django-token-auth
Token Authentication for Bluebottle.

<img src="https://travis-ci.org/onepercentclub/django-token-auth.svg" />


## Configuration

To activate the application, add `token_auth` to your list of installed apps:

    INSTALLED_APPS = [
         .....,
         token_auth,
    ]

And add the urls in your `urls.py`.

    urlpatterns = patterns('',
        ....
        url(r'token/', include('token_auth.urls')),
        ....


Django token auth can be configured by in your settings:

    TOKEN_AUTH = {
        'backend': 'token_auth.auth.booking.TokenAuthentication',
        'sso_url': 'https://example.org',
        ....
    }

Token auth supports the following settings:

  * backend: The class used for token authentication. Choices are `token_auth.auth.booking.TokenAuthentication`
    or `token_auth.auth.saml.SAMLAuthentication`.
  * sso_url: (booking) location the user should be redirected to for sign on.
  * token_expiration: (booking) time (in seconds) after which a token should be expired. 
  * hmac_key: (booking) Key used for HMAC encryption.
  * aes_key: (booking) Key used for EAS encryption.

Besides that all settings for the python-saml client can be specified here. See https://github.com/onelogin/python-saml

